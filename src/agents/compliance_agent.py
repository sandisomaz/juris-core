import time
import uuid
from src.agents.state import WorkflowState
from src.domain.findings import Finding, SeverityLevel, VerificationStatus
from src.domain.audit import AgentStepTrace

class ComplianceAgent:
    """Compliance Analysis Agent: Interprets legal language, obligation gaps, and risks."""

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()
        findings = []

        # Analyze extracted clauses for high-level legal risks
        for clause in state.clauses:
            text_lower = clause.text.lower()

            # Check unlimited liability
            if "unlimited liability" in text_lower or ("indemnify" in text_lower and "cap" not in text_lower):
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
                    confidence=0.88,
                    explanation="The indemnity obligation does not contain a monetary cap or limitation of liability.",
                    recommended_action="Insert a standard limitation of liability cap tied to 12 months fees.",
                    redline=f"Section {clause.clause_id}. [Limitation of Liability]\nNotwithstanding anything to the contrary, total aggregate liability under this Agreement shall be capped at 12 months' fees paid.",
                    verification_status=VerificationStatus.UNCERTAIN_HUMAN_REVIEW
                ))

            # Check cross-border data transfer
            if "transfer" in text_lower and ("outside south africa" in text_lower or "cross-border" in text_lower):
                if "consent" not in text_lower and "adequate protection" not in text_lower:
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
                        confidence=0.92,
                        explanation="Personal information transfer outside South Africa requires data subject consent or adequate legal protection in recipient jurisdiction under POPIA s72.",
                        recommended_action="Require binding corporate rules or data transfer agreement prior to international processing.",
                        redline=f"Section {clause.clause_id}. [Transborder Data Flows]\nNo Personal Information shall be transferred outside South Africa unless recipient is subject to law establishing adequate level of protection compliant with POPIA Section 72.",
                        verification_status=VerificationStatus.UNCERTAIN_HUMAN_REVIEW
                    ))

        state.ai_findings = findings
        state.current_step = "COMPLIANCE_ANALYSIS_COMPLETED"

        duration = (time.time() - t0) * 1000
        state.step_traces.append(AgentStepTrace(
            agent_name="ComplianceAgent",
            action_summary=f"Identified {len(findings)} potential obligation gaps and risk findings.",
            duration_ms=round(duration, 2),
            details={"findings_count": len(findings)}
        ))
        return state

compliance_agent = ComplianceAgent()
