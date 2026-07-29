from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ComplaintExtractionState
from app.services.groq_client import get_fast_llm, invoke_with_retry
from app.agents.prompts.generate_summary_prompt import GENERATE_SUMMARY_SYSTEM_PROMPT

async def generate_summary_node(state: ComplaintExtractionState) -> dict:
    try:
        llm = get_fast_llm()
        raw_text = state.get("raw_text", "")
        fields = str(state.get("extracted_fields", {}))
        
        messages = [
            SystemMessage(content=GENERATE_SUMMARY_SYSTEM_PROMPT),
            HumanMessage(content=f"Raw text: {raw_text}\nExtracted: {fields}")
        ]
        
        summary = await invoke_with_retry(llm, messages)
        
        return {
            "summary": summary.strip(),
            "current_node": "generate_summary"
        }
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [f"Error in generate_summary: {str(e)}"],
            "current_node": "generate_summary"
        }
