import time
from src.agents.state import WorkflowState
from src.deterministic.rules_engine import deterministic_rules_engine
from src.deterministic.citation_validator import citation_validator, CitationStatus
from src.domain.findings import VerificationStatus
from src.domain.audit import AgentStepTrace

class VerifierAgent:
    """Citation & Rule Verifier Node: Executes deterministic verification layer."""

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()

        # 1. Run deterministic rules engine
        rule_pack = state.rule_pack or deterministic_rules_engine.create_default_popia_rulepack()
        det_findings = deterministic_rules_engine.evaluate_document(state.document_dom, rule_pack)
        state.deterministic_findings = det_findings

        # 2. Combine and verify findings
        combined = []
        for det_f in det_findings:
            combined.append(det_f)

        for ai_f in state.ai_findings:
            # Check if statutory reference in AI finding is valid
            val_res = citation_validator.validate_citation(ai_f.legal_basis)
            if val_res["status"] == CitationStatus.VALID:
                ai_f.verification_status = VerificationStatus.VERIFIED_PASS
            elif val_res["status"] == CitationStatus.WRONG_SECTION:
                ai_f.verification_status = VerificationStatus.CITATION_WRONG_SECTION
            elif val_res["status"] == CitationStatus.OUTDATED:
                ai_f.verification_status = VerificationStatus.CITATION_OUTDATED
            else:
                ai_f.verification_status = VerificationStatus.UNCERTAIN_HUMAN_REVIEW

            combined.append(ai_f)

        state.final_findings = combined
        state.current_step = "VERIFICATION_COMPLETED"

        duration = (time.time() - t0) * 1000
        state.step_traces.append(AgentStepTrace(
            agent_name="VerifierAgent",
            action_summary=f"Verified {len(combined)} findings against deterministic legal rules engine and citation registry.",
            duration_ms=round(duration, 2),
            details={"deterministic_findings": len(det_findings), "total_findings": len(combined)}
        ))
        return state

verifier_agent = VerifierAgent()
