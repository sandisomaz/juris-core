import re
from typing import List, Dict, Any, Optional, Tuple
from src.domain.documents import Clause
from src.domain.compliance import RuleRequirement, RuleCategory, SeverityLevel

class ClauseRulesChecker:
    """Checks clause presence, missing mandatory terms, and prohibited clauses."""

    def check_clause_presence(self, clauses: List[Clause], required_concept: str, keywords: List[str]) -> Tuple[bool, Optional[Clause]]:
        for clause in clauses:
            text_lower = (clause.title + " " + clause.text).lower()
            if any(kw.lower() in text_lower for kw in keywords):
                return True, clause
        return False, None

    def check_prohibited_terms(self, clause: Clause, prohibited_keywords: List[str]) -> List[str]:
        found = []
        text_lower = (clause.title + " " + clause.text).lower()
        for kw in prohibited_keywords:
            if kw.lower() in text_lower:
                found.append(kw)
        return found
