from typing import TypedDict, Annotated
import operator

class ComplaintExtractionState(TypedDict):
    raw_text: str
    source_file_type: str
    extracted_fields: dict
    field_confidence: dict
    missing_fields: list[str]
    completeness_score: float
    severity_classification: dict
    duplicate_candidates: list[dict]
    summary: str
    errors: list[str]
    current_node: str
    run_id: str
    complaint_id: str
    progress_callbacks: list
