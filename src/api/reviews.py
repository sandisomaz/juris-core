import uuid
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.agents.supervisor import supervisor_orchestrator
from src.domain.findings import Finding, HumanDecision, VerificationStatus
from src.domain.audit import AgentRunTrace, AuditEvent
from src.api.documents import IN_MEMORY_DOCUMENTS, RAW_DOC_CONTENTS
from src.deterministic.scoring import compliance_scorer
from src.domain.reports import ComplianceReport, ReviewSummary

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

IN_MEMORY_FINDINGS: Dict[str, Finding] = {}
IN_MEMORY_TRACES: Dict[str, AgentRunTrace] = {}
IN_MEMORY_AUDIT_LOGS: List[AuditEvent] = []
IN_MEMORY_REPORTS: Dict[str, ComplianceReport] = {}

class StartReviewRequest(BaseModel):
    matter_id: str
    document_id: str

class HumanDecisionRequest(BaseModel):
    finding_id: str
    decision: HumanDecision
    notes: Optional[str] = None

@router.post("/run", response_model=ComplianceReport)
async def run_review(req: StartReviewRequest):
    # Retrieve raw document text or load sample
    target_doc = next((d for d in IN_MEMORY_DOCUMENTS if d.id == req.document_id), None)
    raw_text = RAW_DOC_CONTENTS.get(req.document_id, "")

    if not raw_text and target_doc:
        raw_text = "\n\n".join([f"{c.title}\n{c.text}" for c in target_doc.clauses])

    if not raw_text:
        # Generate standard contract text for demo if none uploaded yet
        raw_text = """MASTER SERVICES AND DATA PROCESSING AGREEMENT

1. DEFINITIONS AND JURISDICTION
This Master Services Agreement is entered into under the jurisdiction of South Africa.

2. OPERATOR OBLIGATIONS AND SECURITY
The Operator agrees to process Personal Information on behalf of the Responsible Party. The Operator shall maintain confidential treatment of all data.

3. SECURITY INCIDENT NOTIFICATION
In the event of a security compromise or data breach, the Operator shall notify the Responsible Party in writing within 120 hours of becoming aware of such incident.

4. LIMITATION OF LIABILITY AND INDEMNITY
The Supplier provides an indemnity to the Customer for all losses. There shall be unlimited liability exposure without any financial cap.

5. STATUTORY GOVERNING LAW
This agreement references POPIA Section 22 and Companies Act Section 66.
"""
        if target_doc:
            RAW_DOC_CONTENTS[req.document_id] = raw_text

    # Execute Supervised Agent Workflow
    state, trace = supervisor_orchestrator.run_workflow(
        matter_id=req.matter_id,
        document_id=req.document_id,
        filename=target_doc.filename if target_doc else "sample_contract.txt",
        content=raw_text
    )

    # Save trace
    IN_MEMORY_TRACES[trace.trace_id] = trace

    # Save findings
    for f in state.final_findings:
        IN_MEMORY_FINDINGS[f.finding_id] = f

    # Generate summary metrics
    summary = compliance_scorer.calculate_summary(
        total_clauses=len(state.clauses) if state.clauses else 5,
        findings=state.final_findings
    )

    report_id = f"rep-{uuid.uuid4().hex[:6]}"
    report = ComplianceReport(
        report_id=report_id,
        matter_id=req.matter_id,
        document_id=req.document_id,
        summary=summary,
        findings=state.final_findings,
        executive_memo=f"Automated multi-agent legal review completed under {state.jurisdiction} jurisdiction. Identified {len(state.final_findings)} items requiring legal attention.",
        agent_trace_id=trace.trace_id
    )

    IN_MEMORY_REPORTS[report_id] = report
    return report

@router.get("/findings", response_model=List[Finding])
async def list_findings(document_id: Optional[str] = None):
    if document_id:
        return [f for f in IN_MEMORY_FINDINGS.values() if f.document_id == document_id]
    return list(IN_MEMORY_FINDINGS.values())

@router.post("/decision", response_model=Finding)
async def record_human_decision(req: HumanDecisionRequest):
    finding = IN_MEMORY_FINDINGS.get(req.finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding.human_decision = req.decision
    finding.reviewer_notes = req.notes

    # Create immutable audit log
    audit_evt = AuditEvent(
        event_id=f"evt-{uuid.uuid4().hex[:6]}",
        matter_id=finding.matter_id,
        document_id=finding.document_id,
        finding_id=finding.finding_id,
        action=f"HUMAN_DECISION_{req.decision.value}",
        actor="Senior Legal Counsel",
        details={"notes": req.notes, "issue": finding.issue}
    )
    IN_MEMORY_AUDIT_LOGS.append(audit_evt)
    return finding
