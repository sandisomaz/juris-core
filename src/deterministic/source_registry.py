from datetime import date
from typing import Dict, List, Optional
from pydantic import BaseModel

class LegalSourceEntry(BaseModel):
    jurisdiction: str
    legislation: str
    act_number: str
    year: int
    section: str
    subsection: Optional[str] = None
    official_title: str
    effective_date: str
    source_url: str
    requirements_summary: str
    is_active: bool = True

class LegalSourceRegistry:
    """Deterministic Legal Source Registry holding verified statutory data."""

    def __init__(self):
        self._sources: Dict[str, LegalSourceEntry] = {}
        self._populate_defaults()

    def _populate_defaults(self):
        # POPIA - Protection of Personal Information Act 4 of 2013
        popia_s19 = LegalSourceEntry(
            jurisdiction="South Africa",
            legislation="POPIA",
            act_number="Act 4 of 2013",
            year=2013,
            section="19",
            official_title="Security measures on integrity and confidentiality of personal information",
            effective_date="2020-07-01",
            source_url="https://www.gov.za/documents/protection-personal-information-act",
            requirements_summary="Responsible party must secure integrity and confidentiality of personal information by taking appropriate, reasonable technical and organisational measures."
        )
        popia_s21 = LegalSourceEntry(
            jurisdiction="South Africa",
            legislation="POPIA",
            act_number="Act 4 of 2013",
            year=2013,
            section="21",
            official_title="Operator functions and written agreement",
            effective_date="2020-07-01",
            source_url="https://www.gov.za/documents/protection-personal-information-act",
            requirements_summary="An operator must process personal information only with the knowledge or authorisation of the responsible party and treat personal information as confidential. Requires written contract establishing obligations."
        )
        popia_s22 = LegalSourceEntry(
            jurisdiction="South Africa",
            legislation="POPIA",
            act_number="Act 4 of 2013",
            year=2013,
            section="22",
            official_title="Notification of security compromises",
            effective_date="2020-07-01",
            source_url="https://www.gov.za/documents/protection-personal-information-act",
            requirements_summary="Where there are reasonable grounds to believe personal information has been accessed or acquired by unauthorised person, responsible party must notify Information Regulator and data subject as soon as reasonably possible."
        )

        # Companies Act 71 of 2008
        companies_s66 = LegalSourceEntry(
            jurisdiction="South Africa",
            legislation="Companies Act",
            act_number="Act 71 of 2008",
            year=2008,
            section="66",
            official_title="Board, directors and prescribed officers",
            effective_date="2011-05-01",
            source_url="https://www.gov.za/documents/companies-act",
            requirements_summary="The business and affairs of a company must be managed by or under the direction of its board."
        )

        # GDPR
        gdpr_art28 = LegalSourceEntry(
            jurisdiction="European Union",
            legislation="GDPR",
            act_number="Regulation (EU) 2016/679",
            year=2016,
            section="Article 28",
            official_title="Processor obligations",
            effective_date="2018-05-25",
            source_url="https://eur-lex.europa.eu/eli/reg/2016/679/oj",
            requirements_summary="Processing by a processor shall be governed by a contract setting out subject-matter, duration, nature, purpose, type of personal data, and categories of data subjects."
        )

        self._sources["POPIA:s19"] = popia_s19
        self._sources["POPIA:s21"] = popia_s21
        self._sources["POPIA:s22"] = popia_s22
        self._sources["COMPANIES:s66"] = companies_s66
        self._sources["GDPR:art28"] = gdpr_art28

    def lookup(self, legislation: str, section: str) -> Optional[LegalSourceEntry]:
        key = f"{legislation.upper()}:{section.lower().replace('section ', 's').replace('art ', 'art')}"
        # Direct lookup
        for k, entry in self._sources.items():
            if entry.legislation.upper() in legislation.upper() and entry.section.lower() in section.lower():
                return entry
        return None

    def search_sources(self, query: str) -> List[LegalSourceEntry]:
        results = []
        q = query.lower()
        for source in self._sources.values():
            if q in source.legislation.lower() or q in source.official_title.lower() or q in source.requirements_summary.lower():
                results.append(source)
        return results

    def get_all_sources(self) -> List[LegalSourceEntry]:
        return list(self._sources.values())

source_registry = LegalSourceRegistry()
