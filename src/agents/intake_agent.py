import time
from src.agents.state import WorkflowState
from src.domain.documents import DocumentType
from src.domain.audit import AgentStepTrace

class IntakeAgent:
    """Intake Agent: Classifies document type and jurisdiction."""

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()
        text_lower = state.raw_content.lower()

        doc_type = DocumentType.CONTRACT
        if "policy" in text_lower or "privacy notice" in text_lower:
            doc_type = DocumentType.POLICY
        elif "addendum" in text_lower or "data processing" in text_lower:
            doc_type = DocumentType.CONTRACT
        elif "supplier" in text_lower or "onboarding" in text_lower:
            doc_type = DocumentType.SUPPLIER_FORM

        jurisdiction = "South Africa"
        if "gdpr" in text_lower or "european union" in text_lower:
            jurisdiction = "European Union / South Africa"

        state.document_type = doc_type
        state.jurisdiction = jurisdiction
        state.current_step = "INTAKE_COMPLETED"

        duration = (time.time() - t0) * 1000
        state.step_traces.append(AgentStepTrace(
            agent_name="IntakeAgent",
            action_summary=f"Classified document as {doc_type.value} under {jurisdiction} jurisdiction.",
            duration_ms=round(duration, 2),
            details={"doc_type": doc_type.value, "jurisdiction": jurisdiction}
        ))
        return state

intake_agent = IntakeAgent()
