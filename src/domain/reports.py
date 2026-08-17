from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.domain.findings import Finding, SeverityLevel

class ReviewSummary(BaseModel):
    total_clauses_analyzed: int = 0
    passed_count: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    compliance_score: float = 0.0

class ComplianceReport(BaseModel):
    report_id: str
    matter_id: str
    document_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    summary: ReviewSummary
    findings: List[Finding] = Field(default_factory=list)
    executive_memo: str = ""
    agent_trace_id: str = ""
