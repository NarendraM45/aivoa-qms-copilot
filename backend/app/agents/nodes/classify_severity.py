import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ComplaintExtractionState
from app.services.groq_client import get_fast_llm, invoke_with_retry
from app.agents.prompts.classify_severity_prompt import CLASSIFY_SEVERITY_SYSTEM_PROMPT

async def classify_severity_node(state: ComplaintExtractionState) -> dict:
    try:
        llm = get_fast_llm()
        desc = state.get("extracted_fields", {}).get("complaint_description", "")
        prod = state.get("extracted_fields", {}).get("product_name", "")
        content = f"Product: {prod}\nDescription: {desc}"
        
        messages = [
            SystemMessage(content=CLASSIFY_SEVERITY_SYSTEM_PROMPT),
            HumanMessage(content=content)
        ]
        
        response_text = await invoke_with_retry(llm, messages)
        
        json_str = response_text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
            
        data = json.loads(json_str)
        return {
            "severity_classification": data,
            "current_node": "classify_severity"
        }
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [f"Error in classify_severity: {str(e)}"],
            "current_node": "classify_severity"
        }
