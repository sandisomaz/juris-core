import io
import zipfile
from datetime import datetime, timezone
from src.domain.reports import ComplianceReport


def generate_docx_document(report: ComplianceReport) -> bytes:
    """Generates a native Microsoft Word (.docx) document containing executive findings and redlines."""
    
    # WordprocessingML XML content
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Title"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:b/>
          <w:color w:val="002045"/>
          <w:sz w:val="36"/>
        </w:rPr>
        <w:t>JurisCore Executive Compliance Memorandum</w:t>
      </w:r>
    </w:p>
    
    <w:p>
      <w:r>
        <w:rPr>
          <w:color w:val="74777F"/>
          <w:sz w:val="20"/>
        </w:rPr>
        <w:t>Report ID: {report.report_id} | Matter: {report.matter_id} | Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</w:t>
      </w:r>
    </w:p>
    
    <w:p><w:r><w:t></w:t></w:r></w:p>
    
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading1"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:b/>
          <w:color w:val="002045"/>
          <w:sz w:val="28"/>
        </w:rPr>
        <w:t>1. Executive Summary &amp; Compliance Score</w:t>
      </w:r>
    </w:p>
    
    <w:p>
      <w:r>
        <w:rPr><w:b/><w:sz w:val="22"/></w:rPr>
        <w:t>Overall Compliance Score: {report.summary.compliance_score}% | High Risk Items: {report.summary.high_risk_count} | Compliant Clauses: {report.summary.passed_count}</w:t>
      </w:r>
    </w:p>
    
    <w:p>
      <w:r>
        <w:rPr><w:sz w:val="22"/></w:rPr>
        <w:t>{report.executive_memo}</w:t>
      </w:r>
    </w:p>
    
    <w:p><w:r><w:t></w:t></w:r></w:p>
    
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading1"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:b/>
          <w:color w:val="002045"/>
          <w:sz w:val="28"/>
        </w:rPr>
        <w:t>2. Detailed Findings &amp; Surgical Redlines (Track Changes)</w:t>
      </w:r>
    </w:p>
"""

    for idx, f in enumerate(report.findings, start=1):
        redline_escaped = (f.redline or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ")
        explanation_escaped = (f.explanation or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        action_escaped = (f.recommended_action or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        document_xml += f"""
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading2"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:b/>
          <w:color w:val="BA1A1A"/>
          <w:sz w:val="24"/>
        </w:rPr>
        <w:t>Finding {idx}: {f.issue} [{f.severity.value}]</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:rPr><w:i/><w:color w:val="43474E"/><w:sz w:val="20"/></w:rPr>
        <w:t>Location: {f.location} | Legal Basis: {f.legal_basis}</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:rPr><w:sz w:val="22"/></w:rPr>
        <w:t>Analysis: {explanation_escaped}</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:rPr><w:b/><w:color w:val="006A63"/><w:sz w:val="22"/></w:rPr>
        <w:t>Recommended Action: {action_escaped}</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:rPr><w:b/><w:sz w:val="20"/></w:rPr>
        <w:t>Proposed Contract Amendment (Track Changes Replacement):</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:rPr><w:color w:val="002045"/><w:sz w:val="20"/></w:rPr>
        <w:t>{redline_escaped}</w:t>
      </w:r>
    </w:p>
    <w:p><w:r><w:t></w:t></w:r></w:p>
"""

    document_xml += """
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
    </w:sectPr>
  </w:body>
</w:document>
"""

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    # Pack into standard .docx ZIP archive
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types_xml)
        docx.writestr('_rels/.rels', rels_xml)
        docx.writestr('word/document.xml', document_xml)

    return buffer.getvalue()
