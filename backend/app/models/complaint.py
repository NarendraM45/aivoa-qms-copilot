import uuid
from sqlalchemy import Column, String, Date, Numeric, Text, JSON, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String(30), nullable=False, default='pending_triage')
    complaint_source = Column(String(50))
    customer_name = Column(String(255))
    product_name = Column(String(255))
    product_strength = Column(String(100))
    batch_number = Column(String(100))
    manufacturing_date = Column(Date)
    expiry_date = Column(Date)
    quantity_affected = Column(Numeric(12, 2))
    quantity_unit = Column(String(20))
    complaint_type = Column(String(100))
    complaint_date = Column(Date)
    complaint_description = Column(Text)
    initial_severity = Column(String(20))
    priority = Column(String(20))
    ai_extraction_confidence = Column(JSONB)
    ai_summary = Column(Text)
    source_document_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    created_by = Column(String(255))

    attachments = relationship("ComplaintAttachment", back_populates="complaint", cascade="all, delete-orphan")
    extraction_runs = relationship("AIExtractionRun", back_populates="complaint", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="complaint", cascade="all, delete-orphan")
    duplicate_matches = relationship("DuplicateMatch", foreign_keys="[DuplicateMatch.complaint_id]", back_populates="complaint", cascade="all, delete-orphan")
    capa_recommendations = relationship("CAPARecommendation", back_populates="complaint", cascade="all, delete-orphan")
    audit_trails = relationship("AuditTrail", back_populates="complaint", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_complaints_batch_number', batch_number),
        Index('idx_complaints_product_name', product_name),
        Index('idx_complaints_status', status),
        Index('idx_complaints_complaint_date', complaint_date),
    )
