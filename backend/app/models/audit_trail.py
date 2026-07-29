import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey('complaints.id', ondelete='CASCADE'))
    action = Column(String(100))
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    performed_by = Column(String(255))
    performed_at = Column(DateTime(timezone=True), default=func.now())

    complaint = relationship("Complaint", back_populates="audit_trails")
