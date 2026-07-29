from app.agents.state import ComplaintExtractionState

async def parse_document_node(state: ComplaintExtractionState) -> dict:
    """Clean up raw text by stripping excessive whitespace and normalizing line endings."""
    try:
        raw_text = state.get("raw_text", "")
        # Clean text
        cleaned = "\n".join(line.strip() for line in raw_text.splitlines() if line.strip())
        return {
            "raw_text": cleaned,
            "current_node": "parse_document"
        }
    except Exception as e:
        return {
            "errors": state.get("errors", []) + [f"Error in parse_document: {str(e)}"],
            "current_node": "parse_document"
        }
