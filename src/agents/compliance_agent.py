import time
import uuid
from typing import List, Dict, Optional
from src.agents.state import WorkflowState
from src.domain.documents import Clause
from src.domain.findings import Finding, SeverityLevel, VerificationStatus
from src.domain.audit import AgentStepTrace
from src.core.llm_bridge import llm_bridge


class ComplianceAgent:
    """Compliance Analysis Agent: Interprets legal obligations and cross-document contract conflicts."""

    def _evaluate_cross_document_conflicts(self, state: WorkflowState) -> List[Finding]:
        """Cross-examines clauses across all matter sources to detect conflicting terms."""
        cross_findings = []
        if len(state.clauses) < 2:
            return cross_findings

        # Collect clause texts
        clauses_by_title = {c.title.lower(): c for c in state.clauses}
        clauses_text_lower = " ".join([c.text.lower() for c in state.clauses])

        # 1. Cross-Document Notice SLA Contradiction
        sla_clauses = [c for c in state.clauses if "hour" in c.text.lower() or "day" in c.text.lower() or "breach" in c.text.lower()]
        if len(sla_clauses) >= 2:
            # Check for conflicting SLA timelines (e.g., 120h vs 24h)
            texts = [c.text.lower() for c in sla_clauses]
            has_120h = any("120" in t for t in texts)
            has_24h = any("24" in t or "immediate" in t or "without undue delay" in t for t in texts)
            if has_120h and has_24h:
                c1, c2 = sla_clauses[0], sla_clauses[1]
                cross_findings.append(Finding(
                    finding_id=f"cross-{uuid.uuid4().hex[:8]}",
                    document_id=state.document_id,
                    matter_id=state.matter_id,
                    clause_id=c1.clause_id,
                    location=f"Cross-Document Conflict: Clause {c1.clause_id} vs Clause {c2.clause_id}",
                    issue="Conflicting Security Breach Notification SLAs",
                    severity=SeverityLevel.HIGH,
                    legal_basis="POPIA Section 22 / Contract Harmony",
                    source="Cross-Document Reconciliation",
                    confidence=0.96,
                    explanation=(
                        f"Master Agreement and Security Addendum define contradictory breach notification timelines "
                        f"('{c1.title}' vs '{c2.title}'). POPIA Section 22 requires notification as soon as reasonably possible."
                    ),
                    recommended_action="Harmonize breach notification timeline to a single standard of 24-48 hours across all schedules.",
                    redline="In the event of a security incident or breach, the Operator shall notify Customer without undue delay and within 24 hours.",
                    related_sources=[state.filename],
                    conflicting_clause_ids=[c1.clause_id, c2.clause_id],
                    verification_status=VerificationStatus.UNCERTAIN_HUMAN_REVIEW
                ))

        # 2. Cross-Document Liability Cap Super-Priority Conflict
        indemnity_clauses = [c for c in state.clauses if "indemn" in c.text.lower() or "liabilit" in c.text.lower()]
        if len(indemnity_clauses) >= 2:
            has_cap = any("cap" in c.text.lower() or "maximum" in c.text.lower() or "limited" in c.text.lower() for c in indemnity_clauses)
            has_uncapped = any("unlimited" in c.text.lower() or "notwithstanding" in c.text.lower() for c in indemnity_clauses)
            if has_cap and has_uncapped:
                c_main = indemnity_clauses[0]
                cross_findings.append(Finding(
                    finding_id=f"cross-{uuid.uuid4().hex[:8]}",
                    document_id=state.document_id,
                    matter_id=state.matter_id,
                    clause_id=c_main.clause_id,
                    location=f"Cross-Document Conflict: Liability Hierarchy",
                    issue="DPA Liability Carve-Out Overrides MSA Cap",
                    severity=SeverityLevel.HIGH,
                    legal_basis="Commercial Risk Policy",
                    source="Cross-Document Reconciliation",
                    confidence=0.93,
                    explanation="The Data Processing Addendum contains a super-priority carve-out that un-caps data protection liability, bypassing the aggregate cap in the Master Agreement.",
                    recommended_action="Explicitly define whether data protection indemnities are subject to a standalone super-cap (e.g. 2x annual contract value).",
                    redline="Total aggregate liability for Data Protection Breaches under this Addendum shall be subject to a super-cap of 2x the Annual Contract Value.",
                    related_sources=[state.filename],
                    conflicting_clause_ids=[c.clause_id for c in indemnity_clauses],
                    verification_status=VerificationStatus.UNCERTAIN_HUMAN_REVIEW
                ))

        return cross_findings

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()
        findings = []

        system_prompt = (
            "You are an expert legal AI compliance agent. You must review the provided clause and determine if it violates the specified rule. "
            "Return ONLY a JSON object with keys: 'violation_found' (boolean), 'reasoning' (string), and 'suggested_redline' (string)."
        )

        # 1. Analyze individual clauses for compliance violations
        for clause in state.clauses:
            text_lower = clause.text.lower()

            # Check unlimited liability
            if "unlimited liability" in text_lower or ("indemnify" in text_lower and "cap" not in text_lower):
                user_prompt = f"Rule: The indemnity obligation must contain a monetary cap or limitation of liability.\nClause Text: {clause.text}"
                resp = llm_bridge.query(system_prompt, user_prompt, expect_json=True)
                
                if resp.get("violation_found", True):
                    findings.append(Finding(
                        finding_id=f"ai-{uuid.uuid4().hex[:8]}",
                        document_id=state.document_id,
                        matter_id=state.matter_id,
                        clause_id=clause.clause_id,
                        location=f"Clause {clause.clause_id} ({clause.title})",
                        issue="Uncapped Liability Exposure",
                        severity=SeverityLevel.HIGH,
                        legal_basis="Contractual Risk Standard / Firm Policy",
                        source="AI Compliance Agent Analysis",
                        confidence=0.92,
                        explanation=resp.get("reasoning", "The indemnity obligation does not contain a monetary cap or limitation of liability."),
                        recommended_action="Insert a standard limitation of liability cap tied to 12 months fees.",
                        redline=resp.get("suggested_redline", f"Section {clause.clause_id}. [Limitation of Liability]\nNotwithstanding anything to the contrary, total aggregate liability under this Agreement shall be capped at 12 months' fees paid."),
                        related_sources=[state.filename],
                        verification_status=VerificationStatus.UNCERTAIN_HUMAN_REVIEW
                    ))

            # Check cross-border data transfer
            if "transfer" in text_lower and ("outside south africa" in text_lower or "cross-border" in text_lower):
                if "consent" not in text_lower and "adequate protection" not in text_lower:
                    user_prompt = f"Rule: Personal information transfer outside South Africa requires data subject consent or adequate legal protection in recipient jurisdiction under POPIA s72.\nClause Text: {clause.text}"
                    resp = llm_bridge.query(system_prompt, user_prompt, expect_json=True)

                    if resp.get("violation_found", True):
                        findings.append(Finding(
                            finding_id=f"ai-{uuid.uuid4().hex[:8]}",
                            document_id=state.document_id,
                            matter_id=state.matter_id,
                            clause_id=clause.clause_id,
                            location=f"Clause {clause.clause_id} ({clause.title})",
                            issue="Unrestricted Cross-Border Data Transfer",
                            severity=SeverityLevel.HIGH,
                            legal_basis="POPIA Section 72",
                            source="POPIA Statutory Framework",
                            confidence=0.95,
                            explanation=resp.get("reasoning", "Personal information transfer outside South Africa requires data subject consent or adequate legal protection in recipient jurisdiction under POPIA s72."),
                            recommended_action="Require binding corporate rules or data transfer agreement prior to international processing.",
                            redline=resp.get("suggested_redline", f"Section {clause.clause_id}. [Transborder Data Flows]\nNo Personal Information shall be transferred outside South Africa unless recipient is subject to law establishing adequate level of protection compliant with POPIA Section 72."),
                            related_sources=[state.filename],
                            verification_status=VerificationStatus.UNCERTAIN_HUMAN_REVIEW
                        ))

        # 2. Check cross-document reconciliation and conflicts
        cross_findings = self._evaluate_cross_document_conflicts(state)
        findings.extend(cross_findings)

        state.ai_findings = findings
        state.current_step = "COMPLIANCE_ANALYSIS_COMPLETED"

        duration = (time.time() - t0) * 1000
        state.step_traces.append(AgentStepTrace(
            agent_name="ComplianceAgent",
            action_summary=f"Identified {len(findings)} potential obligation gaps, risks, and cross-document conflicts.",
            duration_ms=round(duration, 2),
            details={"findings_count": len(findings), "cross_conflicts_count": len(cross_findings)}
        ))
        return state


compliance_agent = ComplianceAgent()
