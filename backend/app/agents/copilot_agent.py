"""LangGraph-based AI Copilot agent for complaint management.

Uses a ReAct-style agent with tool calling to:
1. Log new complaints from natural language descriptions
2. Edit existing complaints from user corrections
3. Extract complaint data from uploaded documents

The agent uses llama-3.3-70b-versatile on Groq for fast inference.
"""
import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from app.services.groq_client import get_fast_llm
from app.agents.tools.complaint_tools import COPILOT_TOOLS

logger = logging.getLogger(__name__)

COPILOT_SYSTEM_PROMPT = """You are AIVOA, an AI co-pilot for pharmaceutical Quality Management System (QMS) complaint handling.

Your role is to help quality assurance professionals log, edit, and manage customer complaints about API (Active Pharmaceutical Ingredient) and FDF (Finished Dosage Form) products.

You have two tools:

1. **log_complaint** — Use when the user describes a NEW complaint. Extract ALL relevant fields from their message: product name, strength, batch number, dates, quantities, complaint type, description, etc. Also assess the risk: determine severity (minor/major/critical), priority (low/medium/high/urgent), recommended next action, and provide justification.

2. **edit_complaint** — Use when the user wants to CORRECT or UPDATE specific fields of an already-logged complaint. Only provide the fields that need to change. Example: "Sorry, the batch number is BMX24602" → only update batch_number.

Rules:
- ALWAYS use a tool when the user provides complaint information or corrections. Never just respond with text when you should be updating the form.
- complaint_source must be one of: phone, email, letter, portal, sales_rep
- complaint_type must be one of: product_quality, packaging, adverse_event, delivery, documentation, other
- severity: minor (cosmetic/packaging only), major (quality defect affecting product), critical (adverse event, health risk, or patient safety concern)
- priority: low (minor + small quantity), medium (major + contained), high (major + widespread), urgent (critical or patient safety)
- Normalize dates to YYYY-MM-DD format
- Only extract what is explicitly stated. Never fabricate values.
- For risk assessment: consider complaint type, severity keywords (discoloration, contamination, adverse reaction), quantity affected, and patient exposure.
- next_action examples: "Route to QA investigation", "Issue replacement and investigate", "Initiate field alert", "Quarantine batch and investigate", "File adverse event report"
- When the user uploads a document, extract ALL information from it just like a log_complaint.
- After logging or editing, confirm what you did in your response message.
- If the user asks a question (not providing complaint data), respond helpfully WITHOUT calling a tool.

Current form state (for context when editing):
{current_form_state}
"""


async def run_copilot(
    user_message: str,
    conversation_history: list[dict] = None,
    current_form_state: dict = None,
) -> dict:
    """Run the copilot agent on a user message.
    
    Returns dict with keys:
    - message: str (AI response text)
    - field_updates: dict (form field updates)
    - risk_assessment: dict (severity, priority, next_action, etc.)
    - action: str (log | edit | none)
    """
    if conversation_history is None:
        conversation_history = []
    if current_form_state is None:
        current_form_state = {}
    
    llm = get_fast_llm()
    llm_with_tools = llm.bind_tools(COPILOT_TOOLS)
    
    # Build system prompt with current form state
    form_state_str = json.dumps(current_form_state, indent=2, default=str) if current_form_state else "{}"
    system_prompt = COPILOT_SYSTEM_PROMPT.replace("{current_form_state}", form_state_str)
    
    # Build message list
    messages = [SystemMessage(content=system_prompt)]
    
    # Add conversation history
    for msg in conversation_history[-10:]:  # Keep last 10 messages for context
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    
    # Add the current user message
    messages.append(HumanMessage(content=user_message))
    
    try:
        # First LLM call — may include tool calls
        response = await llm_with_tools.ainvoke(messages)
        
        # Check if the LLM wants to call a tool
        if response.tool_calls:
            # Process tool calls
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Find and execute the tool
                tool_fn = None
                for t in COPILOT_TOOLS:
                    if t.name == tool_name:
                        tool_fn = t
                        break
                
                if tool_fn:
                    result = tool_fn.invoke(tool_args)
                    tool_results.append({
                        "call": tool_call,
                        "result": result,
                    })
            
            # Parse tool results
            merged_field_updates = {}
            merged_risk_assessment = {}
            action = "none"
            
            for tr in tool_results:
                try:
                    result_data = json.loads(tr["result"])
                    merged_field_updates.update(result_data.get("field_updates", {}))
                    merged_risk_assessment.update(result_data.get("risk_assessment", {}))
                    action = result_data.get("action", action)
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Could not parse tool result: {tr['result']}")
            
            # Second LLM call — get human-readable response with tool results
            messages.append(response)
            for tr in tool_results:
                messages.append(
                    ToolMessage(
                        content=tr["result"],
                        tool_call_id=tr["call"]["id"],
                    )
                )
            
            follow_up = await llm.ainvoke(messages)
            response_message = follow_up.content or "Done."
            
            return {
                "message": response_message,
                "field_updates": merged_field_updates,
                "risk_assessment": merged_risk_assessment,
                "action": action,
            }
        else:
            # No tool call — just a conversational response
            return {
                "message": response.content or "I'm here to help with complaint management. Please describe a complaint or ask a question.",
                "field_updates": {},
                "risk_assessment": {},
                "action": "none",
            }
    
    except Exception as e:
        logger.error(f"Copilot agent error: {type(e).__name__}: {e}")
        return {
            "message": f"I encountered an error processing your request: {str(e)}. Please try again.",
            "field_updates": {},
            "risk_assessment": {},
            "action": "none",
        }
