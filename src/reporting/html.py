from jinja2 import Template
from src.domain.reports import ComplianceReport

HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>JurisCore Compliance Review Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }
        .container { max-width: 960px; margin: 0 auto; background: #1e293b; padding: 40px; border-radius: 12px; border: 1px solid #334155; }
        h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 12px; margin-top: 0; }
        .summary-card { display: flex; gap: 20px; margin: 24px 0; background: #0f172a; padding: 20px; border-radius: 8px; }
        .metric { flex: 1; text-align: center; }
        .metric-val { font-size: 28px; font-weight: bold; color: #38bdf8; }
        .metric-lbl { font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-top: 4px; }
        .finding { background: #0f172a; border-left: 4px solid #ef4444; margin-bottom: 20px; padding: 20px; border-radius: 6px; }
        .finding.high { border-left-color: #ef4444; }
        .finding.medium { border-left-color: #f97316; }
        .finding.low { border-left-color: #3b82f6; }
        .issue-title { font-size: 18px; font-weight: bold; margin-bottom: 8px; color: #f1f5f9; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; background: #334155; color: #f8fafc; }
        .badge.critical, .badge.high { background: #7f1d1d; color: #fca5a5; }
        .badge.medium { background: #7c2d12; color: #fdba74; }
        .badge.verified { background: #14532d; color: #86efac; }
        .legal-basis { font-size: 13px; color: #94a3b8; margin: 6px 0; }
        .explanation { font-size: 14px; margin: 12px 0; line-height: 1.5; color: #cbd5e1; }
        .redline-box { background: #1e293b; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 13px; margin-top: 10px; border: 1px dashed #475569; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚖️ JurisCore Compliance Executive Report</h1>
        <p><strong>Report ID:</strong> {{ report.report_id }} | <strong>Matter ID:</strong> {{ report.matter_id }} | <strong>Generated:</strong> {{ report.generated_at }}</p>
        
        <div class="summary-card">
            <div class="metric">
                <div class="metric-val">{{ report.summary.compliance_score }}%</div>
                <div class="metric-lbl">Compliance Score</div>
            </div>
            <div class="metric">
                <div class="metric-val" style="color: #ef4444;">{{ report.summary.high_risk_count }}</div>
                <div class="metric-lbl">High Risk Issues</div>
            </div>
            <div class="metric">
                <div class="metric-val" style="color: #f97316;">{{ report.summary.medium_risk_count }}</div>
                <div class="metric-lbl">Medium Risk Issues</div>
            </div>
            <div class="metric">
                <div class="metric-val" style="color: #22c55e;">{{ report.summary.passed_count }}</div>
                <div class="metric-lbl">Passed Clauses</div>
            </div>
        </div>

        <h2>Executive Summary</h2>
        <p style="line-height: 1.6; color: #cbd5e1;">{{ report.executive_memo }}</p>

        <h2>Detailed Compliance Findings</h2>
        {% for f in report.findings %}
        <div class="finding {{ f.severity.value.lower() }}">
            <div class="issue-title">
                {{ f.issue }}
                <span class="badge {{ f.severity.value.lower() }}">{{ f.severity.value }}</span>
                <span class="badge verified">{{ f.verification_status.value }}</span>
            </div>
            <div class="legal-basis">📍 <strong>Location:</strong> {{ f.location }} | ⚖️ <strong>Legal Basis:</strong> {{ f.legal_basis }}</div>
            <div class="explanation"><strong>Analysis:</strong> {{ f.explanation }}</div>
            <div class="explanation">💡 <strong>Recommended Action:</strong> {{ f.recommended_action }}</div>
            {% if f.redline %}
            <div class="redline-box">
                <strong>Proposed Legal Redline:</strong><br/>
                {{ f.redline }}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

def generate_html_report(report: ComplianceReport) -> str:
    template = Template(HTML_REPORT_TEMPLATE)
    return template.render(report=report)
