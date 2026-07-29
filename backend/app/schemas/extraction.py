from typing import Optional, List, Dict
from pydantic import BaseModel

class ComplaintExtractedFields(BaseModel):
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity_affected: Optional[float] = None
    quantity_unit: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    complaint_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None

class FieldConfidence(BaseModel):
    field_name: str
    confidence: float
    source_snippet: Optional[str] = None

class ExtractionResponse(BaseModel):
    run_id: str
    status: str
    extracted_fields: Optional[ComplaintExtractedFields] = None
    field_confidence: Optional[List[FieldConfidence]] = None
    missing_fields: Optional[List[str]] = None
    completeness_score: Optional[float] = None
    severity_classification: Optional[Dict] = None
    summary: Optional[str] = None
    processing_time_ms: Optional[int] = None

class TextExtractionRequest(BaseModel):
    raw_text: str
