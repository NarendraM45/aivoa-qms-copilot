"""Extraction routes for AI-powered complaint field extraction."""
import uuid
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import get_settings
from app.services.file_parser import parse_file
from app.models.extraction_run import AIExtractionRun
from app.agents.graph import run_extraction
from app.schemas.extraction import ExtractionResponse, TextExtractionRequest, ComplaintExtractedFields, FieldConfidence

router = APIRouter(prefix="/api/complaints/extract", tags=["extraction"])


@router.post("/upload", response_model=ExtractionResponse)
async def extract_from_upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a complaint document (PDF/DOCX/TXT/EML) and extract fields via AI."""
    settings = get_settings()

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    allowed = {"pdf", "docx", "txt", "eml"}
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: .{ext}. Allowed: {', '.join(allowed)}",
        )

    try:
        content = await file.read()

        # Validate file size
        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed ({settings.MAX_UPLOAD_MB} MB)",
            )

        raw_text = await parse_file(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

    run_id = str(uuid.uuid4())
    start_time = time.time()

    # Create extraction run record
    ext_run = AIExtractionRun(
        id=uuid.UUID(run_id),
        status="running",
        model_used=settings.GROQ_MODEL_FAST,
    )
    db.add(ext_run)
    await db.commit()

    try:
        final_state = await run_extraction(raw_text, ext, run_id)
        processing_time_ms = int((time.time() - start_time) * 1000)

        has_errors = bool(final_state.get("errors"))
        ext_run.status = "completed" if not has_errors else "failed"
        ext_run.raw_extracted_json = final_state.get("extracted_fields")
        ext_run.confidence_scores = final_state.get("field_confidence")
        ext_run.missing_fields = final_state.get("missing_fields")
        ext_run.processing_time_ms = processing_time_ms
        if has_errors:
            ext_run.error_message = "; ".join(final_state["errors"])
        await db.commit()

        # Build field confidence list
        raw_confidence = final_state.get("field_confidence", [])
        field_confidence = None
        if isinstance(raw_confidence, list):
            field_confidence = [
                FieldConfidence(**fc) if isinstance(fc, dict) else fc
                for fc in raw_confidence
            ]

        # Build extracted fields
        raw_fields = final_state.get("extracted_fields", {})
        extracted_fields = ComplaintExtractedFields(**raw_fields) if raw_fields else None

        return ExtractionResponse(
            run_id=run_id,
            status=ext_run.status,
            extracted_fields=extracted_fields,
            field_confidence=field_confidence,
            missing_fields=final_state.get("missing_fields"),
            completeness_score=final_state.get("completeness_score"),
            severity_classification=final_state.get("severity_classification"),
            summary=final_state.get("summary"),
            processing_time_ms=processing_time_ms,
        )
    except Exception as e:
        ext_run.status = "failed"
        ext_run.error_message = str(e)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/text", response_model=ExtractionResponse)
async def extract_from_text(
    request: TextExtractionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Extract complaint fields from pasted raw text."""
    if not request.raw_text or not request.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text cannot be empty")

    settings = get_settings()
    run_id = str(uuid.uuid4())
    start_time = time.time()

    ext_run = AIExtractionRun(
        id=uuid.UUID(run_id),
        status="running",
        model_used=settings.GROQ_MODEL_FAST,
    )
    db.add(ext_run)
    await db.commit()

    try:
        final_state = await run_extraction(request.raw_text, "txt", run_id)
        processing_time_ms = int((time.time() - start_time) * 1000)

        has_errors = bool(final_state.get("errors"))
        ext_run.status = "completed" if not has_errors else "failed"
        ext_run.raw_extracted_json = final_state.get("extracted_fields")
        ext_run.confidence_scores = final_state.get("field_confidence")
        ext_run.missing_fields = final_state.get("missing_fields")
        ext_run.processing_time_ms = processing_time_ms
        if has_errors:
            ext_run.error_message = "; ".join(final_state["errors"])
        await db.commit()

        raw_confidence = final_state.get("field_confidence", [])
        field_confidence = None
        if isinstance(raw_confidence, list):
            field_confidence = [
                FieldConfidence(**fc) if isinstance(fc, dict) else fc
                for fc in raw_confidence
            ]

        raw_fields = final_state.get("extracted_fields", {})
        extracted_fields = ComplaintExtractedFields(**raw_fields) if raw_fields else None

        return ExtractionResponse(
            run_id=run_id,
            status=ext_run.status,
            extracted_fields=extracted_fields,
            field_confidence=field_confidence,
            missing_fields=final_state.get("missing_fields"),
            completeness_score=final_state.get("completeness_score"),
            severity_classification=final_state.get("severity_classification"),
            summary=final_state.get("summary"),
            processing_time_ms=processing_time_ms,
        )
    except Exception as e:
        ext_run.status = "failed"
        ext_run.error_message = str(e)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
