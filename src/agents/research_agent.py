import time
from src.agents.state import WorkflowState
from src.retrieval.sources import legal_source_provider
from src.domain.audit import AgentStepTrace

class ResearchAgent:
    """Research Agent: Retrieves statutory context and precedent guidance for clauses."""

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()
        contexts = []
        for clause in state.clauses[:5]:
            matches = legal_source_provider.get_context_for_clause(clause.title, clause.text)
            if matches:
                contexts.extend(matches)

        state.research_context = contexts
        state.current_step = "RESEARCH_COMPLETED"

        duration = (time.time() - t0) * 1000
        state.step_traces.append(AgentStepTrace(
            agent_name="ResearchAgent",
            action_summary=f"Retrieved {len(contexts)} statutory legal source contexts with provenance.",
            duration_ms=round(duration, 2),
            details={"sources_found": len(contexts)}
        ))
        return state

research_agent = ResearchAgent()
