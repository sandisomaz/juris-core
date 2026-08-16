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
from src.domain.audit import AgentRunTrace, AgentStepTrace
from src.domain.documents import Document
from src.api.events import sync_broadcast_event


class SupervisorOrchestrator:
    """Supervised Multi-Agent Workflow Supervisor Orchestrator with real-time SSE broadcasting."""

    def _execute_agent_with_events(self, agent_name: str, agent_obj, state: WorkflowState) -> WorkflowState:
        """Executes an agent step and broadcasts real-time SSE event updates."""
        sync_broadcast_event({
            "agent": agent_name,
            "status": "RUNNING",
            "summary": f"{agent_name}: started processing {state.filename or 'matter'}",
            "matter_id": state.matter_id,
            "document_id": state.document_id
        })

        state = agent_obj.execute(state)
        latest_trace: AgentStepTrace = state.step_traces[-1] if state.step_traces else None

        summary = latest_trace.action_summary if latest_trace else f"{agent_name} completed."
        duration_ms = latest_trace.duration_ms if latest_trace else 0.0
        status = "HUMAN_REVIEW_REQUIRED" if agent_name == "EscalationAgent" and state.human_review_required else "COMPLETED"

        sync_broadcast_event({
            "agent": agent_name,
            "status": status,
            "duration_ms": duration_ms,
            "summary": summary,
            "matter_id": state.matter_id,
            "document_id": state.document_id
        })
        return state

    def run_workflow(self, matter_id: str, document_id: str, filename: str, content: str) -> Tuple[WorkflowState, AgentRunTrace]:
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"

        state = WorkflowState(
            trace_id=trace_id,
            matter_id=matter_id,
            document_id=document_id,
            filename=filename,
            raw_content=content
        )

        # Execute Graph Sequence with Live Event Broadcasting
        state = self._execute_agent_with_events("IntakeAgent", intake_agent, state)
        state = self._execute_agent_with_events("ExtractionAgent", extraction_agent, state)
        state = self._execute_agent_with_events("ResearchAgent", research_agent, state)
        state = self._execute_agent_with_events("ComplianceAgent", compliance_agent, state)
        state = self._execute_agent_with_events("VerifierAgent", verifier_agent, state)
        state = self._execute_agent_with_events("RedlineAgent", redline_agent, state)
        state = self._execute_agent_with_events("EscalationAgent", escalation_agent, state)

        total_ms = sum(t.duration_ms for t in state.step_traces)

        run_trace = AgentRunTrace(
            trace_id=trace_id,
            matter_id=matter_id,
            document_id=document_id,
            total_duration_ms=round(total_ms, 2),
            steps=state.step_traces
        )

        return state, run_trace

    def run_matter_workflow(self, matter_id: str, documents: List[Document], raw_contents: Dict[str, str]) -> Tuple[WorkflowState, AgentRunTrace]:
        """Runs the supervised multi-agent pipeline across all documents in a matter."""
        combined_content = ""
        all_clauses = []
        filenames = []

        for doc in documents:
            filenames.append(doc.filename)
            content = raw_contents.get(doc.id, "")
            if not content and doc.clauses:
                content = "\n\n".join([f"{c.title}\n{c.text}" for c in doc.clauses])
            combined_content += f"\n\n--- DOCUMENT: {doc.filename} ---\n{content}"
            all_clauses.extend(doc.clauses)

        matter_filename = " + ".join(filenames) if filenames else "Matter Documents"
        state, trace = self.run_workflow(
            matter_id=matter_id,
            document_id=documents[0].id if documents else "doc-matter",
            filename=matter_filename,
            content=combined_content
        )
        return state, trace


supervisor_orchestrator = SupervisorOrchestrator()
