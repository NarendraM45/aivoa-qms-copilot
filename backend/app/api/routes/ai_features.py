"""AI feature routes: duplicate detection, root cause, CAPA, completeness, risk classification."""
import uuid
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.core.database import get_db
from app.models.complaint import Complaint
from app.models.duplicate_match import DuplicateMatch
from app.models.capa_recommendation import CAPARecommendation
from app.agents.nodes.root_cause_node import suggest_root_causes
from app.agents.nodes.capa_node import recommend_capa
from app.agents.nodes.check_completeness import check_completeness_node
from app.agents.nodes.classify_severity import classify_severity_node
from app.agents.nodes.detect_duplicates import detect_duplicates_node
from app.schemas.ai_features import (
    DuplicateMatchResponse,
    RootCauseSuggestion,
    CAPARecommendationResponse,
    CompletenessCheckResponse,
    RiskClassificationResponse,
)

router = APIRouter(prefix="/api/complaints", tags=["ai-features"])


def _complaint_to_dict(comp: Complaint) -> dict:
    """Convert a Complaint ORM object to a plain dict for AI node consumption."""
    return {
        "product_name": comp.product_name,
        "product_strength": comp.product_strength,
        "batch_number": comp.batch_number,
        "customer_name": comp.customer_name,
        "complaint_source": comp.complaint_source,
        "complaint_type": comp.complaint_type,
        "complaint_date": comp.complaint_date.isoformat() if comp.complaint_date else None,
        "manufacturing_date": comp.manufacturing_date.isoformat() if comp.manufacturing_date else None,
        "expiry_date": comp.expiry_date.isoformat() if comp.expiry_date else None,
        "quantity_affected": float(comp.quantity_affected) if comp.quantity_affected else None,
        "quantity_unit": comp.quantity_unit,
        "complaint_description": comp.complaint_description,
        "initial_severity": comp.initial_severity,
        "priority": comp.priority,
    }


@router.post("/{complaint_id}/check-duplicates", response_model=list[DuplicateMatchResponse])
async def check_duplicates(
    complaint_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run duplicate detection against existing complaints.
    
    Uses a hybrid approach: SQL filter by product/batch first (deterministic),
    then LLM semantic comparison for similarity scoring.
    """
    comp = await db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")

    try:
        state = {
            "extracted_fields": _complaint_to_dict(comp),
            "errors": [],
        }
        result = await detect_duplicates_node(state)

        if result.get("errors"):
            raise HTTPException(status_code=500, detail=str(result["errors"]))

        responses = []
        for dup in result.get("duplicate_candidates", []):
            # Don't flag self as duplicate
            if dup.get("complaint_id") == complaint_id:
                continue

            dm = DuplicateMatch(
                id=uuid.uuid4(),
                complaint_id=complaint_id,
                potential_duplicate_id=dup["complaint_id"],
                similarity_score=dup.get("similarity_score", 0.0),
                match_reason=dup.get("match_reason", ""),
            )
            db.add(dm)
            responses.append(
                DuplicateMatchResponse(
                    id=str(dm.id),
                    potential_duplicate_id=dup["complaint_id"],
                    similarity_score=dup.get("similarity_score", 0.0),
                    match_reason=dup.get("match_reason", ""),
                )
            )

        await db.commit()
        return responses
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Duplicate detection failed: {str(e)}")


@router.post("/{complaint_id}/root-cause-suggestions", response_model=list[RootCauseSuggestion])
async def root_cause_suggestions(
    complaint_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get AI-suggested root causes using Ishikawa/fishbone categories."""
    comp = await db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")

    try:
        suggestions = await suggest_root_causes(_complaint_to_dict(comp))
        return [RootCauseSuggestion(**s) for s in suggestions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Root cause analysis failed: {str(e)}")


@router.post("/{complaint_id}/capa-recommendations", response_model=CAPARecommendationResponse)
async def capa_recommendations(
    complaint_id: str,
    root_cause: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-recommended Corrective and Preventive Actions (CAPA).
    
    Distinguishes corrective (fixes this instance) from preventive (stops recurrence).
    """
    comp = await db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")

    try:
        rec = await recommend_capa(_complaint_to_dict(comp), root_cause)

        capa = CAPARecommendation(
            id=uuid.uuid4(),
            complaint_id=complaint_id,
            root_cause_category=rec.get("root_cause_category"),
            root_cause_text=rec.get("root_cause_text"),
            recommended_corrective_action=rec.get("recommended_corrective_action"),
            recommended_preventive_action=rec.get("recommended_preventive_action"),
            ai_confidence=str(rec.get("ai_confidence", "")),
        )
        db.add(capa)
        await db.commit()

        return CAPARecommendationResponse(
            id=str(capa.id),
            root_cause_category=capa.root_cause_category or "",
            root_cause_text=capa.root_cause_text or "",
            recommended_corrective_action=capa.recommended_corrective_action or "",
            recommended_preventive_action=capa.recommended_preventive_action or "",
            ai_confidence=capa.ai_confidence or "",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CAPA recommendation failed: {str(e)}")


@router.post("/{complaint_id}/completeness-check", response_model=CompletenessCheckResponse)
async def completeness_check(
    complaint_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run a deterministic completeness check on complaint fields."""
    comp = await db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")

    try:
        state = {
            "extracted_fields": _complaint_to_dict(comp),
            "errors": [],
        }
        result = await check_completeness_node(state)

        if result.get("errors"):
            raise HTTPException(status_code=500, detail=str(result["errors"]))

        return CompletenessCheckResponse(
            completeness_score=result.get("completeness_score", 0.0),
            missing_fields=result.get("missing_fields", []),
            suggestions={
                field: f"Please provide {field.replace('_', ' ')}"
                for field in result.get("missing_fields", [])
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Completeness check failed: {str(e)}")


@router.post("/{complaint_id}/risk-classification", response_model=RiskClassificationResponse)
async def risk_classification(
    complaint_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get AI-suggested risk/severity classification for a complaint."""
    comp = await db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")

    try:
        state = {
            "extracted_fields": _complaint_to_dict(comp),
            "errors": [],
        }
        result = await classify_severity_node(state)

        if result.get("errors"):
            raise HTTPException(status_code=500, detail=str(result["errors"]))

        cls_data = result.get("severity_classification", {})
        return RiskClassificationResponse(
            severity=cls_data.get("severity", ""),
            priority=cls_data.get("priority", ""),
            reasoning=cls_data.get("reasoning", ""),
            risk_factors=cls_data.get("risk_factors", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk classification failed: {str(e)}")
