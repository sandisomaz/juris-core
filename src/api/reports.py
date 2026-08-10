from fastapi import APIRouter, HTTPException, Response
from src.api.reviews import IN_MEMORY_REPORTS
from src.reporting.html import generate_html_report
from src.reporting.json import export_report_to_json
from src.domain.reports import ComplianceReport

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/{report_id}", response_model=ComplianceReport)
async def get_report(report_id: str):
    rep = IN_MEMORY_REPORTS.get(report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
    return rep

@router.get("/{report_id}/export/html", response_class=Response)
async def export_html_report(report_id: str):
    rep = IN_MEMORY_REPORTS.get(report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
    html_content = generate_html_report(rep)
    return Response(content=html_content, media_type="text/html")

@router.get("/{report_id}/export/json", response_class=Response)
async def export_json_report(report_id: str):
    rep = IN_MEMORY_REPORTS.get(report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
    json_str = export_report_to_json(rep)
    return Response(content=json_str, media_type="application/json")
