import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class AIExtractionRun(Base):
    __tablename__ = "ai_extraction_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey('complaints.id', ondelete='CASCADE'))
    raw_extracted_json = Column(JSONB)
    model_used = Column(String(100))
    confidence_scores = Column(JSONB)
    missing_fields = Column(JSONB)
    processing_time_ms = Column(Integer)
    status = Column(String(30))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())

    complaint = relationship("Complaint", back_populates="extraction_runs")
