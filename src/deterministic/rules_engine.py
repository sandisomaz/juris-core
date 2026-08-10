import uuid
import re
from typing import List, Dict, Any, Tuple
from src.domain.documents import Document, Clause
from src.domain.compliance import RulePack, RuleRequirement, RuleCategory, SeverityLevel
from src.domain.findings import Finding, VerificationStatus
from src.deterministic.clause_rules import ClauseRulesChecker
from src.deterministic.date_rules import date_rules_checker
from src.deterministic.citation_validator import citation_validator, CitationStatus

class DeterministicRulesEngine:
    """Core Deterministic Verification Rules Engine."""

    def __init__(self):
        self.clause_checker = ClauseRulesChecker()

    def create_default_popia_rulepack(self) -> RulePack:
        return RulePack(
            pack_id="POPIA_DEFAULT_v1",
            name="POPIA (Protection of Personal Information Act) Compliance Pack",
            jurisdiction="South Africa",
            description="Mandatory compliance checks for POPIA Section 19 (Security), Section 21 (Operator Contracts), Section 22 (Breach Notification).",
            rules=[
                RuleRequirement(
                    rule_id="POPIA-001",
                    title="Operator Confidentiality & Knowledge Obligation",
                    category=RuleCategory.MANDATORY_CLAUSE,
                    severity=SeverityLevel.HIGH,
                    description="Requires operator to process personal information only with knowledge or authorization of responsible party (s21(1)).",
                    mandatory_keywords=["confidential", "authorization", "written consent", "knowledge"],
                    statutory_reference="POPIA Section 21"
                ),
                RuleRequirement(
                    rule_id="POPIA-002",
                    title="Security Incident Notification SLA",
                    category=RuleCategory.TIMEFRAME_SLA,
                    severity=SeverityLevel.CRITICAL,
                    description="Requires operator to notify responsible party immediately / within 24 hours of security compromise (s22).",
                    mandatory_keywords=["breach", "security incident", "compromise", "notify"],
                    max_timeframe_hours=72,
                    statutory_reference="POPIA Section 22"
                ),
                RuleRequirement(
                    rule_id="POPIA-003",
                    title="Security Measures Integrity Obligation",
                    category=RuleCategory.MANDATORY_CLAUSE,
                    severity=SeverityLevel.HIGH,
                    description="Mandatory technical and organizational security measures clause (s19).",
                    mandatory_keywords=["technical measures", "organizational measures", "encryption", "safeguard"],
                    statutory_reference="POPIA Section 19"
                ),
                RuleRequirement(
                    rule_id="POPIA-004",
                    title="Statutory Citation Verification",
                    category=RuleCategory.STATUTORY_CITATION,
                    severity=SeverityLevel.MEDIUM,
                    description="Validates all statutory citations against POPIA Act 4 of 2013.",
                    mandatory_keywords=["POPIA", "Act 4 of 2013"],
                    statutory_reference="POPIA Section 22"
                )
            ]
        )

    def evaluate_document(self, doc: Document, rule_pack: RulePack) -> List[Finding]:
        findings: List[Finding] = []

        for rule in rule_pack.rules:
            if rule.category == RuleCategory.MANDATORY_CLAUSE:
                found, matching_clause = self.clause_checker.check_clause_presence(
                    doc.clauses, rule.title, rule.mandatory_keywords
                )
                if not found:
                    findings.append(Finding(
                        finding_id=f"det-{uuid.uuid4().hex[:8]}",
                        document_id=doc.id,
                        matter_id=doc.matter_id,
                        clause_id=None,
                        location="Entire Document",
                        issue=f"Missing Mandatory Clause: {rule.title}",
                        severity=rule.severity,
                        legal_basis=rule.statutory_reference or "Deterministic Policy Rule",
                        source="JurisCore Deterministic Engine",
                        confidence=1.0,
                        explanation=f"No clause found in document containing required mandatory terms: {', '.join(rule.mandatory_keywords)}.",
                        recommended_action=f"Insert standard compliant clause addressing {rule.title}.",
                        redline=f"Section X. [{rule.title}]\nParty shall ensure {', '.join(rule.mandatory_keywords[:3])} in accordance with {rule.statutory_reference}.",
                        verification_status=VerificationStatus.VERIFIED_FAIL
                    ))
                else:
                    # Check for prohibited terms in matching clause
                    if rule.prohibited_keywords:
                        prohibited_found = self.clause_checker.check_prohibited_terms(matching_clause, rule.prohibited_keywords)
                        if prohibited_found:
                            findings.append(Finding(
                                finding_id=f"det-{uuid.uuid4().hex[:8]}",
                                document_id=doc.id,
                                matter_id=doc.matter_id,
                                clause_id=matching_clause.clause_id,
                                location=f"Clause {matching_clause.clause_id} ({matching_clause.title})",
                                issue=f"Prohibited Language Detected: {rule.title}",
                                severity=rule.severity,
                                legal_basis=rule.statutory_reference or "Deterministic Policy Rule",
                                source="JurisCore Deterministic Engine",
                                confidence=1.0,
                                explanation=f"Clause contains prohibited terms: {', '.join(prohibited_found)}.",
                                recommended_action=f"Remove prohibited language '{', '.join(prohibited_found)}' from Clause {matching_clause.clause_id}.",
                                redline=matching_clause.text.replace(prohibited_found[0], "[REMOVED]"),
                                verification_status=VerificationStatus.VERIFIED_FAIL
                            ))

            elif rule.category == RuleCategory.TIMEFRAME_SLA:
                found, matching_clause = self.clause_checker.check_clause_presence(
                    doc.clauses, rule.title, rule.mandatory_keywords
                )
                if not found:
                    findings.append(Finding(
                        finding_id=f"det-{uuid.uuid4().hex[:8]}",
                        document_id=doc.id,
                        matter_id=doc.matter_id,
                        clause_id=None,
                        location="Entire Document",
                        issue=f"Missing Breach Notification SLA: {rule.title}",
                        severity=SeverityLevel.CRITICAL,
                        legal_basis=rule.statutory_reference or "POPIA Section 22",
                        source="JurisCore Deterministic Engine",
                        confidence=1.0,
                        explanation=f"No security breach notification clause with mandatory keywords ({', '.join(rule.mandatory_keywords)}) was detected.",
                        recommended_action="Add an explicit security breach notification clause with a strict 24-48 hour notification window.",
                        redline="Section X. [Security Incident Notification]\nProcessor shall notify Controller without undue delay and in any event within 24 hours of becoming aware of any Security Incident.",
                        verification_status=VerificationStatus.VERIFIED_FAIL
                    ))
                else:
                    max_allowed = rule.max_timeframe_hours or 72
                    passed, extracted_hours, msg = date_rules_checker.verify_sla_compliance(
                        matching_clause.text, max_allowed
                    )
                    if not passed:
                        findings.append(Finding(
                            finding_id=f"det-{uuid.uuid4().hex[:8]}",
                            document_id=doc.id,
                            matter_id=doc.matter_id,
                            clause_id=matching_clause.clause_id,
                            location=f"Clause {matching_clause.clause_id} ({matching_clause.title})",
                            issue=f"Defective Breach SLA Timeline: {rule.title}",
                            severity=SeverityLevel.HIGH,
                            legal_basis=rule.statutory_reference or "POPIA Section 22",
                            source="JurisCore Deterministic Engine",
                            confidence=1.0,
                            explanation=msg,
                            recommended_action=f"Amend Clause {matching_clause.clause_id} to specify notification within 24 hours.",
                            redline=re.sub(date_rules_checker.HOUR_PATTERNS[0], "within 24 hours", matching_clause.text),
                            verification_status=VerificationStatus.PARTIAL_COMPLIANCE if extracted_hours else VerificationStatus.VERIFIED_FAIL
                        ))

            elif rule.category == RuleCategory.STATUTORY_CITATION:
                # Scan entire document text for statutory references and validate
                for clause in doc.clauses:
                    if "POPIA" in clause.text or "Act 4 of 2013" in clause.text or "Section" in clause.text:
                        val_res = citation_validator.validate_citation(clause.text, expected_context=clause.title)
                        if val_res["status"] != CitationStatus.VALID and val_res["status"] != CitationStatus.UNVERIFIED:
                            findings.append(Finding(
                                finding_id=f"det-{uuid.uuid4().hex[:8]}",
                                document_id=doc.id,
                                matter_id=doc.matter_id,
                                clause_id=clause.clause_id,
                                location=f"Clause {clause.clause_id} ({clause.title})",
                                issue=f"Invalid Statutory Citation: {val_res['legislation']} s{val_res['section']}",
                                severity=SeverityLevel.MEDIUM,
                                legal_basis=f"{val_res['legislation']} s{val_res['section']}",
                                source="JurisCore Citation Validator",
                                confidence=1.0,
                                explanation=val_res["details"],
                                recommended_action="Correct statutory citation to reference official active act and section.",
                                redline=None,
                                verification_status=VerificationStatus.CITATION_WRONG_SECTION if val_res["status"] == CitationStatus.WRONG_SECTION else VerificationStatus.CITATION_OUTDATED
                            ))

        return findings

deterministic_rules_engine = DeterministicRulesEngine()
