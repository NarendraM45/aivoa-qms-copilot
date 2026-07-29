from datetime import date, datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class ComplaintBase(BaseModel):
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    quantity_affected: Optional[float] = None
    quantity_unit: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[date] = None
    complaint_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintUpdate(ComplaintBase):
    pass

class ComplaintResponse(ComplaintBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    ai_summary: Optional[str] = None
    ai_extraction_confidence: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class ComplaintListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[ComplaintResponse]

class AuditTrailResponse(BaseModel):
    id: UUID
    complaint_id: UUID
    action: Optional[str] = None
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    performed_by: Optional[str] = None
    performed_at: datetime

    model_config = ConfigDict(from_attributes=True)
