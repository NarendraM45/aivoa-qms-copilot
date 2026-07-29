from typing import Optional, List, Dict
from pydantic import BaseModel
from app.schemas.complaint import ComplaintResponse

class DuplicateMatchResponse(BaseModel):
    id: str
    potential_duplicate_id: str
    similarity_score: float
    match_reason: str
    duplicate_complaint: Optional[ComplaintResponse] = None

class RootCauseSuggestion(BaseModel):
    root_cause_category: str
    root_cause_text: str
    ai_confidence: str

class CAPARecommendationResponse(BaseModel):
    id: str
    root_cause_category: str
    root_cause_text: str
    recommended_corrective_action: str
    recommended_preventive_action: str
    ai_confidence: str

class CompletenessCheckResponse(BaseModel):
    completeness_score: float
    missing_fields: List[str]
    suggestions: Dict[str, str]

class RiskClassificationResponse(BaseModel):
    severity: str
    priority: str
    reasoning: str
    risk_factors: List[str]
