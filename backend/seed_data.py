import asyncio
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import get_settings
from app.models.complaint import Complaint
from app.models.audit_trail import AuditTrail
from app.core.database import init_db

async def seed():
    await init_db()
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        complaint1 = Complaint(
            product_name="Amoxiclav 625 Tablets",
            batch_number="AMX-2026-0417",
            complaint_source="email",
            customer_name="Priya Nair, Sunrise Hospital Pharmacy",
            complaint_type="product_quality",
            complaint_date=date(2026, 7, 18),
            manufacturing_date=date(2026, 2, 1),
            expiry_date=date(2028, 1, 31),
            quantity_affected=40.0,
            quantity_unit="tablets",
            initial_severity="medium",
            priority="medium",
            status="pending_triage",
            complaint_description="""Subject: Complaint – Discoloration observed in Amoxiclav 625 Tablets, Batch AMX-2026-0417
On July 18, 2026, our pharmacy staff noticed that approximately 40 tablets from
Batch No. AMX-2026-0417 (Mfg Date: 02/2026, Exp Date: 01/2028) showed visible
yellowish discoloration and slight surface chipping on one edge. The affected
strips were part of a shipment of 500 tablets received on July 10, 2026.
No adverse patient reactions have been reported; affected stock has been
quarantined and not dispensed.
Regards,
Priya Nair, Quality Pharmacist, Sunrise Hospital Pharmacy"""
        )
        
        complaint2 = Complaint(
            product_name="Amoxiclav 625 Tablets",
            batch_number="AMX-2026-0417",
            complaint_source="email",
            customer_name="Rakesh Verma, City Care Pharmacy",
            complaint_type="product_quality",
            complaint_date=date(2026, 7, 12),
            quantity_affected=17.0,
            quantity_unit="tablets",
            initial_severity="medium",
            priority="medium",
            status="pending_triage",
            complaint_description="""Subject: Quality issue – Amoxiclav 625, same batch as before?
We received Amoxiclav 625 Tablets Batch AMX-2026-0417 last week and noticed
some tablets are yellowish and chipped at the edges — around 15-20 tablets out
of a strip of 100. Batch received 12 July 2026.
Rakesh Verma, City Care Pharmacy"""
        )
        
        session.add(complaint1)
        session.add(complaint2)
        await session.flush()
        
        audit1 = AuditTrail(
            complaint_id=complaint1.id,
            action="created",
            performed_by="seed_script"
        )
        audit2 = AuditTrail(
            complaint_id=complaint2.id,
            action="created",
            performed_by="seed_script"
        )
        
        session.add(audit1)
        session.add(audit2)
        
        await session.commit()
        print("Data seeded successfully!")
        
if __name__ == "__main__":
    asyncio.run(seed())
