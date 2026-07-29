import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class CAPARecommendation(Base):
    __tablename__ = "capa_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey('complaints.id', ondelete='CASCADE'))
    root_cause_category = Column(String(100))
    root_cause_text = Column(Text)
    recommended_corrective_action = Column(Text)
    recommended_preventive_action = Column(Text)
    ai_confidence = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=func.now())

    complaint = relationship("Complaint", back_populates="capa_recommendations")
