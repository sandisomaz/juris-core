import re
from enum import Enum
from typing import Dict, Any, Optional, Tuple
from src.deterministic.source_registry import source_registry

class CitationStatus(str, Enum):
    VALID = "VALID"
    OUTDATED = "VALID BUT OUTDATED"
    WRONG_SECTION = "VALID CITATION / WRONG SECTION"
    UNKNOWN = "UNKNOWN"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTING = "CONFLICTING"

class CitationValidationResult(Dict[str, Any]):
    status: CitationStatus
    legislation: str
    section: str
    official_title: Optional[str]
    details: str

class CitationValidator:
    """Deterministic statutory citation validator."""

    PATTERNS = [
        # Match "POPIA Section 22" or "Section 21 of POPIA"
        r"(?P<legislation>POPIA|Protection of Personal Information Act|Companies Act|GDPR|Consumer Protection Act)\s+(?:Section|s|Article|art\.?)\s*(?P<section>\d+|[A-Za-z0-9]+)",
        r"(?:Section|s|Article|art\.?)\s*(?P<section>\d+|[A-Za-z0-9]+)\s+of\s+(?:the\s+)?(?P<legislation>POPIA|Protection of Personal Information Act|Companies Act|GDPR|Consumer Protection Act)",
    ]

    def validate_citation(self, citation_text: str, expected_context: Optional[str] = None) -> CitationValidationResult:
        if not citation_text:
            return {
                "status": CitationStatus.UNVERIFIED,
                "legislation": "N/A",
                "section": "N/A",
                "official_title": None,
                "details": "Empty citation provided."
            }

        matched_leg = None
        matched_sec = None

        for pattern in self.PATTERNS:
            match = re.search(pattern, citation_text, re.IGNORECASE)
            if match:
                matched_leg = match.group("legislation")
                matched_sec = match.group("section")
                break

        if not matched_leg or not matched_sec:
            return {
                "status": CitationStatus.UNKNOWN,
                "legislation": citation_text,
                "section": "Unknown",
                "official_title": None,
                "details": f"Citation format '{citation_text}' could not be matched to official legal registry."
            }

        # Normalize legislation name
        leg_normalized = matched_leg.upper()
        if "PROTECTION OF PERSONAL INFORMATION" in leg_normalized:
            leg_normalized = "POPIA"

        # Lookup in source registry
        source_entry = source_registry.lookup(leg_normalized, matched_sec)

        if not source_entry:
            # Check if legislation exists but section is wrong
            all_sources = source_registry.get_all_sources()
            leg_exists = any(s.legislation.upper() == leg_normalized for s in all_sources)
            if leg_exists:
                return {
                    "status": CitationStatus.WRONG_SECTION,
                    "legislation": leg_normalized,
                    "section": matched_sec,
                    "official_title": None,
                    "details": f"{leg_normalized} exists in Legal Source Registry, but Section {matched_sec} is not a valid or recognized statutory section."
                }

            return {
                "status": CitationStatus.UNVERIFIED,
                "legislation": leg_normalized,
                "section": matched_sec,
                "official_title": None,
                "details": f"Statutory reference to {leg_normalized} s{matched_sec} requires human verification against gazetted amendments."
            }

        # Validate context matching if provided
        if expected_context:
            context_lower = expected_context.lower()
            summary_words = [w.lower() for w in source_entry.requirements_summary.split() if len(w) > 4]
            matches = [w for w in summary_words if w in context_lower]
            if len(matches) == 0:
                return {
                    "status": CitationStatus.WRONG_SECTION,
                    "legislation": source_entry.legislation,
                    "section": source_entry.section,
                    "official_title": source_entry.official_title,
                    "details": f"Citation points to valid {source_entry.legislation} s{source_entry.section}, but clause context does not relate to '{source_entry.official_title}'."
                }

        return {
            "status": CitationStatus.VALID,
            "legislation": source_entry.legislation,
            "section": source_entry.section,
            "official_title": source_entry.official_title,
            "details": f"Verified against official registry: {source_entry.act_number} ({source_entry.official_title})."
        }

citation_validator = CitationValidator()
