from app.agents.state import ComplaintExtractionState

async def check_completeness_node(state: ComplaintExtractionState) -> dict:
    try:
        fields = state.get("extracted_fields", {})
        required = ["product_name", "batch_number", "complaint_description", "complaint_type", "complaint_date"]
        important = ["customer_name", "complaint_source", "manufacturing_date", "expiry_date"]
        
        missing = []
        for f in required + important:
            val = fields.get(f)
            if val is None or str(val).strip() == "":
                missing.append(f)
                
        total = len(required) + len(important)
        filled = total - len(missing)
        score = filled / total if total > 0 else 0.0
        
        return {
            "missing_fields": missing,
            "completeness_score": score,
            "current_node": "check_completeness"
        }
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [f"Error in check_completeness: {str(e)}"],
            "current_node": "check_completeness"
        }
