"""
privilege_detector.py

Tiered privilege and confidentiality detector for legal documents:
1. Fast regex sweep for privilege / confidentiality terms.
2. LLM confirmation pass to filter out generic boilerplate from genuine sensitive documents.
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from src.core.llm_bridge import llm_bridge


PRIVILEGE_KEYWORDS = [
    r"\bprivileged\b",
    r"\bwithout prejudice\b",
    r"\battorney[\s-]client privilege\b",
    r"\blegal professional privilege\b",
    r"\bconfidential\b",
    r"\bstrictly confidential\b",
    r"\bnot for distribution\b",
    r"\bfor internal use only\b",
    r"\blitigation privilege\b",
    r"\bsettlement negotiations\b",
]

PRIVILEGE_RE = re.compile("|".join(PRIVILEGE_KEYWORDS), re.IGNORECASE)


@dataclass
class PrivilegeFlag:
    matched_terms: List[str]
    confirmed: bool = False
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matched_terms": self.matched_terms,
            "confirmed": self.confirmed,
            "reasoning": self.reasoning,
        }


def scan_keywords(text: str) -> Optional[PrivilegeFlag]:
    matches = sorted(set(m.group(0).lower() for m in PRIVILEGE_RE.finditer(text)))
    if not matches:
        return None
    return PrivilegeFlag(matched_terms=matches)


def confirm_privilege_with_llm(flag: PrivilegeFlag, text: str, max_chars: int = 3000) -> PrivilegeFlag:
    """
    Confirms whether the keyword hits reflect genuine privilege/confidentiality markings,
    as opposed to generic boilerplate.
    """
    system_prompt = (
        "You are a careful legal document reviewer. You are told which privilege/confidentiality "
        "keywords were found in a document. Decide whether the document is genuinely privileged, "
        "confidential, or otherwise sensitive and should be handled carefully by a human, as opposed "
        "to containing the words only in a generic boilerplate clause with no real sensitivity. "
        'Respond only with JSON: {"is_privileged": true, "reasoning": "one sentence explanation"}.'
    )
    user_prompt = (
        f"Keywords found: {', '.join(flag.matched_terms)}\n\n"
        f"Document excerpt (truncated):\n{text[:max_chars]}"
    )

    result = llm_bridge.query(system_prompt, user_prompt, expect_json=True)

    if "error" not in result:
        flag.confirmed = bool(result.get("is_privileged", True))
        flag.reasoning = result.get("reasoning", "")
    else:
        # Conservative default: flag on error
        flag.confirmed = True
        flag.reasoning = "LLM confirmation unavailable; flagged conservatively based on keyword match."

    return flag


def detect_privilege(text: str) -> Optional[Dict[str, Any]]:
    """Convenience pipeline function returning dictionary representation if detected."""
    flag = scan_keywords(text)
    if flag:
        flag = confirm_privilege_with_llm(flag, text)
        if flag.confirmed:
            return flag.to_dict()
    return None
