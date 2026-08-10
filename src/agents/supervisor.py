import uuid
from typing import List, Dict, Any, Tuple
from src.agents.state import WorkflowState
from src.agents.intake_agent import intake_agent
from src.agents.extraction_agent import extraction_agent
from src.agents.research_agent import research_agent
from src.agents.compliance_agent import compliance_agent
from src.agents.verifier_agent import verifier_agent
from src.agents.redline_agent import redline_agent
from src.agents.escalation_agent import escalation_agent
from src.domain.audit import AgentRunTrace

class SupervisorOrchestrator:
    """Supervised Multi-Agent Workflow Supervisor Orchestrator."""

    def run_workflow(self, matter_id: str, document_id: str, filename: str, content: str) -> Tuple[WorkflowState, AgentRunTrace]:
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"

        state = WorkflowState(
            trace_id=trace_id,
            matter_id=matter_id,
            document_id=document_id,
            filename=filename,
            raw_content=content
        )

        # Execute Graph Sequence
        state = intake_agent.execute(state)
        state = extraction_agent.execute(state)
        state = research_agent.execute(state)
        state = compliance_agent.execute(state)
        state = verifier_agent.execute(state)
        state = redline_agent.execute(state)
        state = escalation_agent.execute(state)

        total_ms = sum(t.duration_ms for t in state.step_traces)

        run_trace = AgentRunTrace(
            trace_id=trace_id,
            matter_id=matter_id,
            document_id=document_id,
            total_duration_ms=round(total_ms, 2),
            steps=state.step_traces
        )

        return state, run_trace

supervisor_orchestrator = SupervisorOrchestrator()
