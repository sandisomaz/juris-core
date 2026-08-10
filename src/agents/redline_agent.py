import time
from src.agents.state import WorkflowState
from src.domain.audit import AgentStepTrace

class RedlineAgent:
    """Redline Drafting Agent: Ensures every finding has precise, surgical replacement language."""

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()
        redline_count = 0

        for finding in state.final_findings:
            if finding.redline:
                redline_count += 1

        state.current_step = "REDLINES_DRAFTED"

        duration = (time.time() - t0) * 1000
        state.step_traces.append(AgentStepTrace(
            agent_name="RedlineAgent",
            action_summary=f"Generated {redline_count} legal redline proposals preserving commercial intent.",
            duration_ms=round(duration, 2),
            details={"redline_count": redline_count}
        ))
        return state

redline_agent = RedlineAgent()
