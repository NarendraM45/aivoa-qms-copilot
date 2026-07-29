import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class ComplaintAttachment(Base):
    __tablename__ = "complaint_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey('complaints.id', ondelete='CASCADE'))
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_type = Column(String(50))
    uploaded_at = Column(DateTime(timezone=True), default=func.now())

    complaint = relationship("Complaint", back_populates="attachments")
