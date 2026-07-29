"""Chat routes for AI-assisted complaint Q&A."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.complaint import Complaint
from app.models.chat_message import ChatMessage
from app.agents.nodes.chat_node import process_chat
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse, ChatMessageResponse

router = APIRouter(prefix="/api/complaints", tags=["chat"])


@router.post("/{complaint_id}/chat", response_model=ChatResponse)
async def send_chat_message(
    complaint_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a chat message about a specific complaint and get AI response.
    
    The AI assistant answers only from the complaint's stored data.
    It will never fabricate information or make medical/safety determinations.
    """
    try:
        # Validate complaint exists
        comp = await db.get(Complaint, complaint_id)
        if not comp:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Fetch chat history
        history_query = (
            select(ChatMessage)
            .where(ChatMessage.complaint_id == complaint_id)
            .order_by(ChatMessage.created_at)
        )
        history_result = await db.execute(history_query)
        chat_history = [
            {"role": m.role, "content": m.message}
            for m in history_result.scalars().all()
        ]

        # Save user message
        user_msg = ChatMessage(
            id=uuid.uuid4(),
            complaint_id=complaint_id,
            role="user",
            message=request.message,
        )
        db.add(user_msg)
        await db.flush()

        # Build complaint context for the AI
        comp_data = {
            "product_name": comp.product_name,
            "product_strength": comp.product_strength,
            "batch_number": comp.batch_number,
            "customer_name": comp.customer_name,
            "complaint_source": comp.complaint_source,
            "complaint_type": comp.complaint_type,
            "complaint_date": str(comp.complaint_date) if comp.complaint_date else None,
            "manufacturing_date": str(comp.manufacturing_date) if comp.manufacturing_date else None,
            "expiry_date": str(comp.expiry_date) if comp.expiry_date else None,
            "quantity_affected": str(comp.quantity_affected) if comp.quantity_affected else None,
            "quantity_unit": comp.quantity_unit,
            "complaint_description": comp.complaint_description,
            "initial_severity": comp.initial_severity,
            "priority": comp.priority,
            "status": comp.status,
            "ai_summary": comp.ai_summary,
        }

        # Get AI response
        response_text = await process_chat(comp_data, chat_history, request.message)

        # Save assistant response
        bot_msg = ChatMessage(
            id=uuid.uuid4(),
            complaint_id=complaint_id,
            role="assistant",
            message=response_text,
        )
        db.add(bot_msg)
        await db.commit()

        return ChatResponse(
            role="assistant",
            message=response_text,
            created_at=datetime.now(timezone.utc),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/{complaint_id}/chat", response_model=ChatHistoryResponse)
async def get_chat_history(
    complaint_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the full chat history for a complaint."""
    comp = await db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")

    history_query = (
        select(ChatMessage)
        .where(ChatMessage.complaint_id == complaint_id)
        .order_by(ChatMessage.created_at)
    )
    history_result = await db.execute(history_query)
    messages = history_result.scalars().all()

    return ChatHistoryResponse(
        messages=[
            ChatMessageResponse(
                id=str(m.id),
                role=m.role,
                message=m.message,
                created_at=m.created_at,
            )
            for m in messages
        ]
    )
