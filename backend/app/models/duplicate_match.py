import uuid
from sqlalchemy import Column, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class DuplicateMatch(Base):
    __tablename__ = "duplicate_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey('complaints.id', ondelete='CASCADE'))
    potential_duplicate_id = Column(UUID(as_uuid=True), ForeignKey('complaints.id', ondelete='CASCADE'))
    similarity_score = Column(Numeric(4, 3))
    match_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())

    complaint = relationship("Complaint", foreign_keys=[complaint_id], back_populates="duplicate_matches")
    potential_duplicate = relationship("Complaint", foreign_keys=[potential_duplicate_id])
