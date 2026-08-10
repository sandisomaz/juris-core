from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from src.domain.compliance import SeverityLevel

class VerificationStatus(str, Enum):
    VERIFIED_PASS = "VERIFIED_PASS"
    VERIFIED_FAIL = "VERIFIED_FAIL"
    PARTIAL_COMPLIANCE = "PARTIAL_COMPLIANCE"
    CITATION_OUTDATED = "CITATION_OUTDATED"
    CITATION_WRONG_SECTION = "CITATION_WRONG_SECTION"
    UNCERTAIN_HUMAN_REVIEW = "UNCERTAIN_HUMAN_REVIEW"

class HumanDecision(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    ESCALATED = "ESCALATED"

class Finding(BaseModel):
    finding_id: str
    document_id: str
    matter_id: str
    clause_id: Optional[str] = Field(None, description="Exact clause identifier, e.g. 3.4")
    location: str = Field(..., description="Human-readable location, e.g. Clause 3.4 (Page 2, Para 4)")
    issue: str = Field(..., description="Short title of the finding")
    severity: SeverityLevel
    legal_basis: str = Field(..., description="Legislation or rule reference, e.g. POPIA Act 4 of 2013 s19")
    source: str = Field(..., description="Verified statutory or internal policy source")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    explanation: str = Field(..., description="Detailed rationale explaining the finding")
    recommended_action: str = Field(..., description="Actionable recommendation for legal counsel")
    redline: Optional[str] = Field(None, description="Proposed replacement text / redline")
    verification_status: VerificationStatus = VerificationStatus.UNCERTAIN_HUMAN_REVIEW
    human_decision: HumanDecision = HumanDecision.PENDING
    reviewer_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
