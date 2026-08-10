import uuid
from typing import List
from fastapi import APIRouter, HTTPException
from src.domain.matters import Matter, MatterCreate, MatterStatus, MatterRiskLevel

router = APIRouter(prefix="/api/matters", tags=["Matters"])

# In-memory store initialized with sample enterprise matters
IN_MEMORY_MATTERS: List[Matter] = [
    Matter(
        id="mat-001",
        title="Supplier Vendor Onboarding - ABC Logistics",
        client_name="Global Procurement Corp",
        jurisdiction="South Africa",
        description="Review of 2026 Vendor Master Services Agreement & Data Processing Addendum for POPIA Section 19 & 21 compliance.",
        tags=["POPIA", "Procurement", "Supplier Contract"],
        status=MatterStatus.ACTIVE,
        overall_risk=MatterRiskLevel.HIGH,
        document_count=2
    ),
    Matter(
        id="mat-002",
        title="SaaS Infrastructure Review - XYZ Cloud Systems",
        client_name="FinTech Solutions Ltd",
        jurisdiction="South Africa / EU",
        description="Cross-border data transfer review and liability cap evaluation under GDPR Art 28 and POPIA Section 72.",
        tags=["Cloud", "SaaS", "GDPR", "Cross-Border"],
        status=MatterStatus.UNDER_REVIEW,
        overall_risk=MatterRiskLevel.MEDIUM,
        document_count=1
    )
]

@router.get("", response_model=List[Matter])
async def list_matters():
    return IN_MEMORY_MATTERS

@router.get("/{matter_id}", response_model=Matter)
async def get_matter(matter_id: str):
    for m in IN_MEMORY_MATTERS:
        if m.id == matter_id:
            return m
    raise HTTPException(status_code=404, detail="Matter not found")

@router.post("", response_model=Matter)
async def create_matter(req: MatterCreate):
    new_matter = Matter(
        id=f"mat-{uuid.uuid4().hex[:6]}",
        title=req.title,
        client_name=req.client_name,
        jurisdiction=req.jurisdiction,
        description=req.description,
        tags=req.tags
    )
    IN_MEMORY_MATTERS.insert(0, new_matter)
    return new_matter
