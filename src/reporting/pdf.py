from src.domain.reports import ComplianceReport
from src.reporting.html import generate_html_report

def generate_pdf_report_bytes(report: ComplianceReport) -> bytes:
    # Returns HTML content as report bytes format for server export
    html_str = generate_html_report(report)
    return html_str.encode("utf-8")
