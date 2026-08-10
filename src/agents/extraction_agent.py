import time
from src.agents.state import WorkflowState
from src.documents.chunker import legal_clause_chunker
from src.domain.documents import Document
from src.domain.audit import AgentStepTrace

class ExtractionAgent:
    """Extraction Agent: Segments document into structured spatial Clause DOM."""

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()
        clauses = legal_clause_chunker.segment_clauses(state.raw_content)

        doc_dom = Document(
            id=state.document_id,
            filename=state.filename,
            doc_type=state.document_type,
            matter_id=state.matter_id,
            file_size_bytes=len(state.raw_content.encode("utf-8")),
            clause_count=len(clauses),
            clauses=clauses
        )

        state.clauses = clauses
        state.document_dom = doc_dom
        state.current_step = "EXTRACTION_COMPLETED"

        duration = (time.time() - t0) * 1000
        state.step_traces.append(AgentStepTrace(
            agent_name="ExtractionAgent",
            action_summary=f"Extracted {len(clauses)} clauses into Document DOM.",
            duration_ms=round(duration, 2),
            details={"clause_count": len(clauses)}
        ))
        return state

extraction_agent = ExtractionAgent()
