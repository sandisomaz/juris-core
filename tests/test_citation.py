from src.deterministic.citation_validator import citation_validator, CitationStatus

def test_valid_popia_citation():
    res = citation_validator.validate_citation("POPIA Section 22")
    assert res["status"] == CitationStatus.VALID
    assert res["legislation"] == "POPIA"
    assert res["section"] == "22"

def test_wrong_section_citation():
    res = citation_validator.validate_citation("POPIA Section 999")
    assert res["status"] == CitationStatus.WRONG_SECTION

def test_unknown_citation():
    res = citation_validator.validate_citation("Fictional Legal Code Section 1")
    assert res["status"] in (CitationStatus.UNKNOWN, CitationStatus.UNVERIFIED)
