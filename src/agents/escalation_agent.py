import time
from src.agents.state import WorkflowState
from src.domain.findings import SeverityLevel, VerificationStatus
from src.domain.audit import AgentStepTrace

class EscalationAgent:
    """Escalation Agent: Detects uncertainty and flags high-risk items for human decision."""

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()
        needs_human = False

        for finding in state.final_findings:
            if finding.severity in (SeverityLevel.CRITICAL, SeverityLevel.HIGH):
                needs_human = True
            if finding.confidence < 0.90 or finding.verification_status == VerificationStatus.UNCERTAIN_HUMAN_REVIEW:
                needs_human = True

        state.human_review_required = needs_human
        state.is_completed = True
        state.current_step = "COMPLETED"

        duration = (time.time() - t0) * 1000
        state.step_traces.append(AgentStepTrace(
            agent_name="EscalationAgent",
            action_summary=f"Finalized review pipeline. Human oversight required: {needs_human}.",
            duration_ms=round(duration, 2),
            details={"human_review_required": needs_human}
        ))
        return state

escalation_agent = EscalationAgent()
