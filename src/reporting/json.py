import json
from src.domain.reports import ComplianceReport

def export_report_to_json(report: ComplianceReport) -> str:
    return report.model_dump_json(indent=2)
