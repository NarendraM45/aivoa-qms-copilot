import json
from sqlalchemy import select
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ComplaintExtractionState
from app.services.groq_client import get_fast_llm, invoke_with_retry
from app.agents.prompts.detect_duplicates_prompt import DETECT_DUPLICATES_SYSTEM_PROMPT
from app.core.database import async_session_maker
from app.models import Complaint

async def detect_duplicates_node(state: ComplaintExtractionState) -> dict:
    try:
        fields = state.get("extracted_fields", {})
        prod = fields.get("product_name")
        batch = fields.get("batch_number")
        desc = fields.get("complaint_description", "")
        
        if not prod and not batch:
            return {"duplicate_candidates": [], "current_node": "detect_duplicates"}
            
        candidates = []
        async with async_session_maker() as session:
            query = select(Complaint)
            if prod and batch:
                query = query.where((Complaint.product_name == prod) | (Complaint.batch_number == batch))
            elif prod:
                query = query.where(Complaint.product_name == prod)
            else:
                query = query.where(Complaint.batch_number == batch)
                
            query = query.limit(10)
            result = await session.execute(query)
            db_candidates = result.scalars().all()
            
        llm = get_fast_llm()
        for cand in db_candidates:
            cand_desc = cand.complaint_description or ""
            if not cand_desc: continue
            
            content = f"Complaint 1: {desc}\nComplaint 2: {cand_desc}\nProduct: {prod}, Batch: {batch}"
            messages = [
                SystemMessage(content=DETECT_DUPLICATES_SYSTEM_PROMPT),
                HumanMessage(content=content)
            ]
            response_text = await invoke_with_retry(llm, messages)
            
            try:
                json_str = response_text
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0]
                data = json.loads(json_str)
                if data.get("is_duplicate"):
                    candidates.append({
                        "complaint_id": str(cand.id),
                        "similarity_score": data.get("similarity_score", 0.0),
                        "match_reason": data.get("match_reason", "")
                    })
            except Exception:
                pass
                
        return {
            "duplicate_candidates": candidates,
            "current_node": "detect_duplicates"
        }
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [f"Error in detect_duplicates: {str(e)}"],
            "current_node": "detect_duplicates"
        }
