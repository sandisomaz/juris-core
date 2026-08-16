from jinja2 import Template
from src.domain.reports import ComplianceReport

HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>JurisCore Compliance Executive Report</title>
    <style>
        body { font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; background: #faf9fd; color: #1a1c1e; margin: 0; padding: 40px; }
        .container { max-width: 900px; margin: 0 auto; background: #ffffff; padding: 48px; border-radius: 10px; border: 1px solid #e3e2e6; box-shadow: 0 4px 20px rgba(0,32,69,0.05); }
        .header-brand { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #002045; padding-bottom: 16px; margin-bottom: 24px; }
        .brand-title { font-size: 24px; font-weight: 700; color: #002045; }
        .meta-line { font-size: 12px; color: #74777f; font-family: monospace; }
        .summary-card { display: flex; gap: 16px; margin: 24px 0; background: #f4f3f7; padding: 20px; border-radius: 8px; border: 1px solid #e3e2e6; }
        .metric { flex: 1; text-align: center; }
        .metric-val { font-size: 32px; font-weight: bold; color: #002045; }
        .metric-lbl { font-size: 11.5px; color: #74777f; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; font-weight: 600; }
        .finding { background: #ffffff; border: 1px solid #e3e2e6; border-left: 4px solid #ba1a1a; margin-bottom: 20px; padding: 20px; border-radius: 6px; }
        .finding.high { border-left-color: #ba1a1a; }
        .finding.medium { border-left-color: #c6955e; }
        .finding.low { border-left-color: #006a63; }
        .issue-title { font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #002045; display: flex; align-items: center; justify-content: space-between; }
        .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; font-family: monospace; background: #e3e2e6; color: #1a1c1e; }
        .badge.high { background: #ffdad6; color: #ba1a1a; }
        .badge.medium { background: #fbf1e6; color: #c6955e; }
        .badge.verified { background: #e6f5ea; color: #146c2e; }
        .legal-basis { font-size: 12.5px; color: #43474e; margin: 6px 0; font-weight: 500; }
        .explanation { font-size: 13.5px; margin: 12px 0; line-height: 1.6; color: #1a1c1e; }
        .action-box { background: #eafaf8; padding: 12px 16px; border-radius: 6px; font-size: 13px; color: #006a63; border-left: 3px solid #006a63; margin-top: 10px; }
        .redline-box { background: #f4f3f7; padding: 14px; border-radius: 6px; font-family: monospace; font-size: 12.5px; margin-top: 12px; border: 1px dashed #c4c6cf; line-height: 1.5; }
        .footer-note { margin-top: 32px; font-size: 11px; color: #74777f; text-align: center; border-top: 1px solid #e3e2e6; padding-top: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-brand">
            <div>
                <div class="brand-title">JurisCore Executive Compliance Memorandum</div>
                <div style="font-size: 13px; color: #43474e; margin-top: 4px;">Automated Statutory Compliance Review & Redlines</div>
            </div>
            <div class="meta-line">
                Report ID: {{ report.report_id }}<br>
                Matter: {{ report.matter_id }}<br>
                Date: {{ report.generated_at }}
            </div>
        </div>
        
        <div class="summary-card">
            <div class="metric">
                <div class="metric-val" style="color: #c6955e;">{{ report.summary.compliance_score }}%</div>
                <div class="metric-lbl">Compliance Score</div>
            </div>
            <div class="metric">
                <div class="metric-val" style="color: #ba1a1a;">{{ report.summary.high_risk_count }}</div>
                <div class="metric-lbl">High Risk Items</div>
            </div>
            <div class="metric">
                <div class="metric-val" style="color: #c6955e;">{{ report.summary.medium_risk_count }}</div>
                <div class="metric-lbl">Medium Risk Items</div>
            </div>
            <div class="metric">
                <div class="metric-val" style="color: #146c2e;">{{ report.summary.passed_count }}</div>
                <div class="metric-lbl">Compliant Clauses</div>
            </div>
        </div>

        <h3 style="color: #002045; margin-bottom: 8px;">Executive Summary</h3>
        <p style="line-height: 1.65; color: #43474e; font-size: 14px;">{{ report.executive_memo }}</p>

        <h3 style="color: #002045; margin-top: 28px; margin-bottom: 12px;">Detailed Compliance Findings & Redlines</h3>
        {% for f in report.findings %}
        <div class="finding {{ f.severity.value.lower() }}">
            <div class="issue-title">
                <span>{{ f.issue }}</span>
                <div>
                    <span class="badge {{ f.severity.value.lower() }}">{{ f.severity.value }}</span>
                    <span class="badge verified">{{ f.verification_status.value }}</span>
                </div>
            </div>
            <div class="legal-basis">Location: {{ f.location }} | Legal Basis: {{ f.legal_basis }}</div>
            <div class="explanation"><strong>Analysis:</strong> {{ f.explanation }}</div>
            <div class="action-box"><strong>Recommended Action:</strong> {{ f.recommended_action }}</div>
            {% if f.redline %}
            <div class="redline-box">
                <strong>Proposed Replacement Language (Track Changes):</strong><br/>
                {{ f.redline }}
            </div>
            {% endif %}
        </div>
        {% endfor %}

        <div class="footer-note">
            This document was generated by JurisCore Regulatory Intelligence Platform. All findings are anchored to deterministic statutory rules and subject to senior counsel sign-off.
        </div>
    </div>
</body>
</html>
"""

def generate_html_report(report: ComplianceReport) -> str:
    template = Template(HTML_REPORT_TEMPLATE)
    return template.render(report=report)
