from src.documents.parser import document_parser
from src.documents.chunker import legal_clause_chunker

def test_document_parser_and_chunker():
    sample_raw = """1. DEFINITIONS AND SCOPE
This is clause 1 text.

2. DATA PRIVACY AND OBLIGATIONS
This is clause 2 text detailing POPIA compliance.
"""
    clean_text, meta = document_parser.parse_bytes("sample.txt", sample_raw.encode("utf-8"))
    assert "DEFINITIONS" in clean_text

    clauses = legal_clause_chunker.segment_clauses(clean_text)
    assert len(clauses) >= 2
    assert clauses[0].title.startswith("1.")
