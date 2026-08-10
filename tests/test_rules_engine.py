from src.deterministic.rules_engine import deterministic_rules_engine
from src.documents.chunker import legal_clause_chunker
from src.domain.documents import Document, DocumentType

def test_deterministic_breach_sla_evaluation():
    sample_text = """
    SECTION 1. SECURITY INCIDENT
    In the event of a breach, Supplier shall notify Customer within 120 hours.
    """
    clauses = legal_clause_chunker.segment_clauses(sample_text)
    doc = Document(
        id="doc-test-1",
        filename="test.txt",
        doc_type=DocumentType.CONTRACT,
        matter_id="mat-test-1",
        clause_count=len(clauses),
        clauses=clauses
    )

    rule_pack = deterministic_rules_engine.create_default_popia_rulepack()
    findings = deterministic_rules_engine.evaluate_document(doc, rule_pack)

    assert len(findings) > 0
    # Should detect defective SLA hours (120 hours > 72 hours max)
    sla_finding = next((f for f in findings if "Defective Breach SLA" in f.issue or "Missing" in f.issue), None)
    assert sla_finding is not None
    assert sla_finding.confidence == 1.0
