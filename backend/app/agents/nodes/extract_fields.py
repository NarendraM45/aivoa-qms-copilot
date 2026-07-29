import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ComplaintExtractionState
from app.services.groq_client import get_fast_llm, invoke_with_retry
from app.agents.prompts.extract_fields_prompt import EXTRACT_FIELDS_SYSTEM_PROMPT
import re

async def extract_fields_node(state: ComplaintExtractionState) -> dict:
    try:
        llm = get_fast_llm()
        messages = [
            SystemMessage(content=EXTRACT_FIELDS_SYSTEM_PROMPT),
            HumanMessage(content=state.get("raw_text", ""))
        ]
        response_text = await invoke_with_retry(llm, messages)
        
        # Parse JSON
        try:
            # try to extract JSON from markdown block
            json_str = response_text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback regex parsing or error out
            raise ValueError("Failed to parse LLM response as JSON")
            
        return {
            "extracted_fields": data.get("extracted_fields", {}),
            "field_confidence": data.get("field_confidence", {}),
            "current_node": "extract_fields"
        }
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [f"Error in extract_fields: {str(e)}"],
            "current_node": "extract_fields"
        }
