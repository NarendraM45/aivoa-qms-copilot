from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.models.complaint import Complaint
from app.models.audit_trail import AuditTrail
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintResponse, ComplaintListResponse, AuditTrailResponse

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(complaint_in: ComplaintCreate, db: AsyncSession = Depends(get_db)):
    # Server-side validation can be added here if needed
    db_complaint = Complaint(**complaint_in.model_dump(exclude_unset=True))
    db.add(db_complaint)
    await db.flush()  # to get the generated ID
    
    # Audit trail for creation
    audit = AuditTrail(
        complaint_id=db_complaint.id,
        action="created",
        performed_by="system" # placeholder
    )
    db.add(audit)
    await db.commit()
    await db.refresh(db_complaint)
    return db_complaint

@router.get("", response_model=ComplaintListResponse)
async def list_complaints(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    product_name: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Complaint).where(Complaint.status != 'deleted')
    
    if status:
        query = query.where(Complaint.status == status)
    if severity:
        query = query.where(Complaint.initial_severity == severity)
    if product_name:
        query = query.where(Complaint.product_name.ilike(f"%{product_name}%"))
        
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Pagination
    query = query.order_by(desc(Complaint.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return ComplaintListResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=list(items)
    )

@router.get("/{id}", response_model=ComplaintResponse)
async def get_complaint(id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(Complaint).options(
        selectinload(Complaint.attachments),
        selectinload(Complaint.extraction_runs)
    ).where(Complaint.id == id, Complaint.status != 'deleted')
    
    result = await db.execute(query)
    complaint = result.scalar_one_or_none()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    return complaint

@router.put("/{id}", response_model=ComplaintResponse)
async def update_complaint(id: UUID, complaint_in: ComplaintUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Complaint).where(Complaint.id == id, Complaint.status != 'deleted'))
    complaint = result.scalar_one_or_none()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    update_data = complaint_in.model_dump(exclude_unset=True)
    
    # Audit trail comparison
    for field, new_value in update_data.items():
        old_value = getattr(complaint, field)
        if old_value != new_value:
            audit = AuditTrail(
                complaint_id=complaint.id,
                action="updated",
                field_name=field,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value) if new_value is not None else None,
                performed_by="system"
            )
            db.add(audit)
            setattr(complaint, field, new_value)
            
    await db.commit()
    await db.refresh(complaint)
    return complaint

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Complaint).where(Complaint.id == id, Complaint.status != 'deleted'))
    complaint = result.scalar_one_or_none()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    complaint.status = 'deleted'
    audit = AuditTrail(
        complaint_id=complaint.id,
        action="deleted",
        performed_by="system"
    )
    db.add(audit)
    await db.commit()

@router.get("/{id}/audit-trail", response_model=List[AuditTrailResponse])
async def get_audit_trail(id: UUID, db: AsyncSession = Depends(get_db)):
    # Verify complaint exists
    complaint_res = await db.execute(select(Complaint).where(Complaint.id == id))
    if not complaint_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    query = select(AuditTrail).where(AuditTrail.complaint_id == id).order_by(desc(AuditTrail.performed_at))
    result = await db.execute(query)
    return list(result.scalars().all())
