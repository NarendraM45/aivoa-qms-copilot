import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.groq_client import get_reasoning_llm, invoke_with_retry
from app.agents.prompts.capa_prompt import CAPA_SYSTEM_PROMPT

async def recommend_capa(complaint_data: dict, root_cause: str) -> dict:
    """Recommend CAPA using reasoning LLM."""
    try:
        llm = get_reasoning_llm()
        content = f"Complaint Data: {json.dumps(complaint_data)}\nRoot Cause: {root_cause}"
        messages = [
            SystemMessage(content=CAPA_SYSTEM_PROMPT),
            HumanMessage(content=content)
        ]
        
        response_text = await invoke_with_retry(llm, messages)
        
        json_str = response_text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
            
        data = json.loads(json_str)
        return data
    except Exception as e:
        raise ValueError(f"CAPA recommendation failed: {str(e)}")
