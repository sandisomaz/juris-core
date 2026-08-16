from fastapi import APIRouter, HTTPException, Response
from src.api.reviews import IN_MEMORY_REPORTS
from src.reporting.html import generate_html_report
from src.reporting.json import export_report_to_json
from src.reporting.docx_export import generate_docx_document
from src.domain.reports import ComplianceReport, ReviewSummary
from src.domain.findings import Finding, SeverityLevel, VerificationStatus

router = APIRouter(prefix="/api/reports", tags=["Reports"])


def get_or_create_fallback_report(report_id: str = "default") -> ComplianceReport:
    """Returns the latest in-memory report or generates a default sample report."""
    if IN_MEMORY_REPORTS:
        if report_id in IN_MEMORY_REPORTS:
            return IN_MEMORY_REPORTS[report_id]
        return list(IN_MEMORY_REPORTS.values())[-1]

    # Generate standard fallback report
    findings = [
        Finding(
            finding_id="f-001",
            document_id="doc-001",
            matter_id="m-001",
            clause_id="3.0",
            location="Clause 3.0 (Security Breach Notification)",
            issue="Defective Security Breach Notification SLA",
            severity=SeverityLevel.HIGH,
            legal_basis="POPIA Section 22",
            source="POPIA Compliance Agent",
            confidence=0.96,
            explanation="The agreement allows 120 hours to notify of a data compromise, which violates POPIA s22.",
            recommended_action="Amend notification timeline to 24-48 hours.",
            redline="In the event of a security breach, Operator shall notify Customer without undue delay and in any event within 24 hours.",
            verification_status=VerificationStatus.UNCERTAIN_HUMAN_REVIEW
        ),
        Finding(
            finding_id="f-002",
            document_id="doc-001",
            matter_id="m-001",
            clause_id="4.0",
            location="Clause 4.0 (Indemnity & Liability)",
            issue="Uncapped Liability Exposure",
            severity=SeverityLevel.HIGH,
            legal_basis="Commercial Risk Policy",
            source="Compliance Analysis Agent",
            confidence=0.92,
            explanation="Indemnity clause contains no aggregate financial cap, exposing supplier to unlimited damages.",
            recommended_action="Insert standard limitation of liability cap tied to 12 months fees.",
            redline="Total aggregate liability shall be capped at 12 months fees paid under this Agreement.",
            verification_status=VerificationStatus.UNCERTAIN_HUMAN_REVIEW
        )
    ]
    summary = ReviewSummary(
        total_clauses_reviewed=4,
        passed_count=2,
        high_risk_count=2,
        medium_risk_count=0,
        low_risk_count=0,
        compliance_score=62.0
    )
    return ComplianceReport(
        report_id=report_id,
        matter_id="m-001",
        document_id="doc-001",
        summary=summary,
        findings=findings,
        executive_memo="Compliance audit completed under South African jurisdiction (POPIA Act 4 of 2013). 2 high-risk items require legal remediation.",
        agent_trace_id="trace-001"
    )


@router.get("/{report_id}", response_model=ComplianceReport)
async def get_report(report_id: str):
    return get_or_create_fallback_report(report_id)


@router.get("/{report_id}/export/html", response_class=Response)
async def export_html_report(report_id: str):
    rep = get_or_create_fallback_report(report_id)
    html_content = generate_html_report(rep)
    return Response(content=html_content, media_type="text/html")


@router.get("/{report_id}/export/json", response_class=Response)
async def export_json_report(report_id: str):
    rep = get_or_create_fallback_report(report_id)
    json_str = export_report_to_json(rep)
    return Response(content=json_str, media_type="application/json")


@router.get("/{report_id}/export/docx")
async def export_docx_report(report_id: str):
    rep = get_or_create_fallback_report(report_id)
    docx_bytes = generate_docx_document(rep)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=JurisCore_Compliance_Report_{rep.matter_id}.docx"}
    )
