"""
deadline_detector.py

Tiered deadline and time-sensitive obligation detector:
1. Fast regex sweep for date-like patterns and deadline-signal phrases.
2. LLM pass over flagged context to confirm genuine obligations vs incidental dates.
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from src.core.llm_bridge import llm_bridge


DATE_PATTERNS = [
    r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
]

DEADLINE_SIGNAL_PHRASES = [
    r"\bdeadline\b",
    r"\bdue (?:by|on|no later than)\b",
    r"\bon or before\b",
    r"\bwithin\s+\d+\s+(?:hours|days|business days|court days|weeks|months)\b",
    r"\bmust\s+(?:be\s+)?(?:filed|served|submitted|responded|answered|delivered|notified)\b",
    r"\bnot later than\b",
    r"\bexpir(?:es|y|ation)\b",
    r"\bnotice period\b",
    r"\bfailing which\b",
]

DATE_RE = re.compile("|".join(DATE_PATTERNS), re.IGNORECASE)
SIGNAL_RE = re.compile("|".join(DEADLINE_SIGNAL_PHRASES), re.IGNORECASE)


@dataclass
class DeadlineCandidate:
    snippet: str
    matched_date: Optional[str]
    has_signal_phrase: bool
    confirmed: bool = False
    confidence: str = "unconfirmed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snippet": self.snippet,
            "matched_date": self.matched_date,
            "has_signal_phrase": self.has_signal_phrase,
            "confirmed": self.confirmed,
            "confidence": self.confidence,
        }


def find_candidates(text: str, context_chars: int = 120) -> List[DeadlineCandidate]:
    """Fast regex pass. Returns raw candidates before LLM confirmation."""
    candidates = []
    seen_spans = set()

    for match in DATE_RE.finditer(text):
        start = max(0, match.start() - context_chars)
        end = min(len(text), match.end() + context_chars)
        span_key = (start, end)
        if span_key in seen_spans:
            continue
        seen_spans.add(span_key)

        snippet = text[start:end].replace("\n", " ").strip()
        has_signal = bool(SIGNAL_RE.search(snippet))

        candidates.append(DeadlineCandidate(
            snippet=snippet,
            matched_date=match.group(0),
            has_signal_phrase=has_signal,
        ))

    # Also catch signal phrases with no nearby explicit date (e.g. "within 120 hours")
    for match in SIGNAL_RE.finditer(text):
        start = max(0, match.start() - context_chars)
        end = min(len(text), match.end() + context_chars)
        snippet = text[start:end].replace("\n", " ").strip()
        if not DATE_RE.search(snippet):
            candidates.append(DeadlineCandidate(
                snippet=snippet,
                matched_date=None,
                has_signal_phrase=True,
            ))

    return candidates


def confirm_deadlines_with_llm(candidates: List[DeadlineCandidate]) -> List[DeadlineCandidate]:
    """Second pass: asks the LLM to confirm genuine deadlines vs incidental dates."""
    if not candidates:
        return candidates

    system_prompt = (
        "You are a careful legal document reviewer. You will be shown short "
        "text snippets from a legal document. For each snippet, decide if it "
        "describes a genuine deadline, obligation, or time-sensitive action "
        "item (something a lawyer would need to act on or calendar), as "
        "opposed to an incidental date (e.g. a signature date, a date of "
        "birth, a historical reference). Respond only with JSON in the form: "
        '{"results": [{"index": 0, "is_deadline": true, "confidence": "high"}, ...]}. '
        "Confidence must be one of: high, medium, low."
    )

    numbered = "\n".join(f"[{i}] {c.snippet}" for i, c in enumerate(candidates))
    user_prompt = f"Snippets:\n{numbered}"

    result = llm_bridge.query(system_prompt, user_prompt, expect_json=True)

    if "error" in result:
        # If LLM confirmation fails, leave candidates as unconfirmed rather than dropping
        return candidates

    for item in result.get("results", []):
        idx = item.get("index")
        if idx is not None and isinstance(idx, int) and 0 <= idx < len(candidates):
            candidates[idx].confirmed = bool(item.get("is_deadline", False))
            candidates[idx].confidence = item.get("confidence", "unconfirmed")

    return candidates


def detect_deadlines(text: str) -> List[Dict[str, Any]]:
    """Convenience pipeline function returning confirmed/candidate deadline flags."""
    candidates = find_candidates(text)
    if candidates:
        candidates = confirm_deadlines_with_llm(candidates)
    return [c.to_dict() for c in candidates if c.confirmed or c.has_signal_phrase]
