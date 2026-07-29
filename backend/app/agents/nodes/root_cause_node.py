import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.groq_client import get_reasoning_llm, invoke_with_retry
from app.agents.prompts.root_cause_prompt import ROOT_CAUSE_SYSTEM_PROMPT

async def suggest_root_causes(complaint_data: dict) -> list[dict]:
    """Suggest root causes using reasoning LLM."""
    try:
        llm = get_reasoning_llm()
        messages = [
            SystemMessage(content=ROOT_CAUSE_SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(complaint_data))
        ]
        
        response_text = await invoke_with_retry(llm, messages)
        
        json_str = response_text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
            
        data = json.loads(json_str)
        if isinstance(data, dict) and "root_causes" in data:
            return data["root_causes"]
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        raise ValueError(f"Root cause generation failed: {str(e)}")
