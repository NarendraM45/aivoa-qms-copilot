"""Pydantic schemas for the AI Copilot endpoint."""
from typing import Optional, Any
from pydantic import BaseModel, Field


class RiskAssessment(BaseModel):
    """AI-generated risk assessment for a complaint."""
    severity: Optional[str] = Field(None, description="minor | major | critical")
    priority: Optional[str] = Field(None, description="low | medium | high | urgent")
    next_action: Optional[str] = Field(None, description="Recommended next action")
    justification: Optional[str] = Field(None, description="Why this severity/priority was assigned")
    risk_factors: list[str] = Field(default_factory=list, description="Identified risk factors")


class CopilotRequest(BaseModel):
    """Request to the copilot chat endpoint."""
    message: str = Field(..., description="User's natural language message")
    conversation_history: list[dict] = Field(default_factory=list, description="Previous messages [{role, content}]")
    current_form_state: dict = Field(default_factory=dict, description="Current complaint form field values")


class CopilotResponse(BaseModel):
    """Response from the copilot chat endpoint."""
    message: str = Field(..., description="AI assistant's response message")
    field_updates: dict = Field(default_factory=dict, description="Fields to update on the form {field_name: value}")
    risk_assessment: Optional[RiskAssessment] = None
    action: str = Field(default="none", description="Action taken: log | edit | extract | none")
