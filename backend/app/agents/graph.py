from langgraph.graph import StateGraph, END
from app.agents.state import ComplaintExtractionState
from app.agents.nodes.parse_document import parse_document_node
from app.agents.nodes.extract_fields import extract_fields_node
from app.agents.nodes.check_completeness import check_completeness_node
from app.agents.nodes.classify_severity import classify_severity_node
from app.agents.nodes.detect_duplicates import detect_duplicates_node
from app.agents.nodes.generate_summary import generate_summary_node

# Create graph
graph = StateGraph(ComplaintExtractionState)

def wrap_node_with_callback(node_func, node_name, progress_pct):
    async def wrapper(state: ComplaintExtractionState):
        result = await node_func(state)
        # Call progress callbacks if any
        callbacks = state.get("progress_callbacks", [])
        for cb in callbacks:
            if callable(cb):
                await cb({
                    "node": node_name,
                    "progress_pct": progress_pct,
                    "message": f"Completed {node_name}"
                })
        return result
    return wrapper

graph.add_node("parse_document", wrap_node_with_callback(parse_document_node, "parse_document", 15))
graph.add_node("extract_fields", wrap_node_with_callback(extract_fields_node, "extract_fields", 50))
graph.add_node("check_completeness", wrap_node_with_callback(check_completeness_node, "check_completeness", 65))
graph.add_node("classify_severity", wrap_node_with_callback(classify_severity_node, "classify_severity", 80))
graph.add_node("detect_duplicates", wrap_node_with_callback(detect_duplicates_node, "detect_duplicates", 90))
graph.add_node("generate_summary", wrap_node_with_callback(generate_summary_node, "generate_summary", 100))

graph.set_entry_point("parse_document")
graph.add_edge("parse_document", "extract_fields")
graph.add_edge("extract_fields", "check_completeness")
graph.add_edge("check_completeness", "classify_severity")
graph.add_edge("classify_severity", "detect_duplicates")
graph.add_edge("detect_duplicates", "generate_summary")
graph.add_edge("generate_summary", END)

extraction_graph = graph.compile()

async def run_extraction(raw_text: str, source_file_type: str, run_id: str, progress_callback=None) -> ComplaintExtractionState:
    """Run the extraction graph."""
    callbacks = [progress_callback] if progress_callback else []
    initial_state = {
        "raw_text": raw_text,
        "source_file_type": source_file_type,
        "run_id": run_id,
        "progress_callbacks": callbacks,
        "errors": []
    }
    final_state = await extraction_graph.ainvoke(initial_state)
    return final_state
