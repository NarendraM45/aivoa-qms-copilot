from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.services.groq_client import get_reasoning_llm, invoke_with_retry
from app.agents.prompts.chat_prompt import CHAT_SYSTEM_PROMPT

async def process_chat(complaint_data: dict, chat_history: list, user_message: str) -> str:
    """Process chat message using reasoning LLM and return response."""
    try:
        llm = get_reasoning_llm()
        sys_msg = f"{CHAT_SYSTEM_PROMPT}\nComplaint Data: {complaint_data}"
        messages = [SystemMessage(content=sys_msg)]
        
        for msg in chat_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            else:
                messages.append(AIMessage(content=msg.get("content", "")))
                
        messages.append(HumanMessage(content=user_message))
        
        response = await invoke_with_retry(llm, messages)
        return response
    except Exception as e:
        raise ValueError(f"Chat processing failed: {str(e)}")
