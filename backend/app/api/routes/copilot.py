"""AI Copilot route — single endpoint for chat-driven complaint management.

Supports three interaction modes:
1. Natural language complaint logging (user describes complaint in chat)
2. Complaint editing via corrections ("sorry, batch number is X")
3. Document extraction (user uploads PDF/DOCX/TXT/EML file)
"""
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.agents.copilot_agent import run_copilot
from app.services.file_parser import parse_file
from app.schemas.copilot import CopilotResponse, RiskAssessment

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/copilot", tags=["copilot"])


@router.post("/chat", response_model=CopilotResponse)
async def copilot_chat(
    message: str = Form(""),
    conversation_history: str = Form("[]"),
    current_form_state: str = Form("{}"),
    file: Optional[UploadFile] = File(None),
):
    """AI Copilot chat endpoint.
    
    Accepts a user message and optionally a file upload. The AI agent will:
    - Extract complaint details from natural language or documents
    - Edit specific fields from correction requests
    - Generate risk assessments
    - Return field updates to populate the form
    
    Uses FormData (not JSON) to support file uploads in the same request.
    """
    import json
    
    # Parse JSON strings from form data
    try:
        history = json.loads(conversation_history)
    except (json.JSONDecodeError, TypeError):
        history = []
    
    try:
        form_state = json.loads(current_form_state)
    except (json.JSONDecodeError, TypeError):
        form_state = {}
    
    # If a file is uploaded, parse it and prepend the text to the message
    effective_message = message.strip()
    
    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        allowed = {"pdf", "docx", "txt", "eml"}
        if ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: .{ext}. Allowed: {', '.join(allowed)}",
            )
        
        try:
            content = await file.read()
            max_bytes = 10 * 1024 * 1024  # 10 MB
            if len(content) > max_bytes:
                raise HTTPException(status_code=400, detail="File size exceeds 10 MB limit")
            
            extracted_text = await parse_file(content, file.filename)
            
            if not extracted_text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file")
            
            # Prepend the document text to the user's message
            doc_prefix = f"[UPLOADED DOCUMENT: {file.filename}]\n\n{extracted_text}\n\n"
            if effective_message:
                effective_message = doc_prefix + f"User's additional instructions: {effective_message}"
            else:
                effective_message = doc_prefix + "Please extract all complaint details from this document and log the complaint."
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File parsing error: {e}")
            raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")
    
    if not effective_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Run the copilot agent
    result = await run_copilot(
        user_message=effective_message,
        conversation_history=history,
        current_form_state=form_state,
    )
    
    # Build risk assessment if present
    risk = None
    if result.get("risk_assessment"):
        ra = result["risk_assessment"]
        risk = RiskAssessment(
            severity=ra.get("severity"),
            priority=ra.get("priority"),
            next_action=ra.get("next_action"),
            justification=ra.get("justification"),
            risk_factors=ra.get("risk_factors", []),
        )
    
    return CopilotResponse(
        message=result.get("message", ""),
        field_updates=result.get("field_updates", {}),
        risk_assessment=risk,
        action=result.get("action", "none"),
    )
