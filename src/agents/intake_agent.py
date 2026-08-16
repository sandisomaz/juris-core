import time
from typing import Dict, Any
from src.agents.state import WorkflowState
from src.domain.documents import DocumentType
from src.domain.audit import AgentStepTrace
from src.core.llm_bridge import llm_bridge
from src.deterministic.privilege_detector import detect_privilege
from src.deterministic.deadline_detector import detect_deadlines


class IntakeAgent:
    """Intake & Triage Agent: Classifies document type, jurisdiction, and sweeps for privilege & deadlines."""

    def _classify_with_llm(self, text_excerpt: str) -> Dict[str, Any]:
        system_prompt = (
            "You are a legal document intake specialist. Classify the document type and jurisdiction. "
            "Categories: CONTRACT, POLICY, SUPPLIER_FORM, COURT_FILING, NOTICE, INVOICE, MEMO. "
            "Jurisdiction defaults to 'South Africa' unless other country laws or GDPR are explicitly indicated. "
            'Respond ONLY with JSON: {"document_type": "CONTRACT", "jurisdiction": "South Africa", "confidence": "high"}'
        )
        user_prompt = f"Document sample:\n{text_excerpt[:2000]}"
        result = llm_bridge.query(system_prompt, user_prompt, expect_json=True)
        if "error" not in result and "document_type" in result:
            return result
        return {}

    def execute(self, state: WorkflowState) -> WorkflowState:
        t0 = time.time()
        text_lower = state.raw_content.lower()

        # 1. Tier 1: Deterministic fast heuristics
        doc_type = DocumentType.CONTRACT
        if "policy" in text_lower or "privacy notice" in text_lower:
            doc_type = DocumentType.POLICY
        elif "supplier" in text_lower or "onboarding" in text_lower:
            doc_type = DocumentType.SUPPLIER_FORM
        elif "addendum" in text_lower or "agreement" in text_lower or "contract" in text_lower:
            doc_type = DocumentType.CONTRACT

        jurisdiction = "South Africa"
        if "gdpr" in text_lower or "european union" in text_lower:
            jurisdiction = "European Union / South Africa"

        # 2. Tier 2: LLM Classification pass if document type is ambiguous or for validation
        llm_classification = self._classify_with_llm(state.raw_content)
        if llm_classification:
            candidate_type = llm_classification.get("document_type", "").upper()
            if candidate_type in DocumentType.__members__:
                doc_type = DocumentType[candidate_type]
            if llm_classification.get("jurisdiction"):
                jurisdiction = llm_classification.get("jurisdiction")

        state.document_type = doc_type
        state.jurisdiction = jurisdiction

        # 3. Triage Sweeps: Privilege & Deadlines
        state.privilege_flag = detect_privilege(state.raw_content)
        state.deadline_flags = detect_deadlines(state.raw_content)

        state.current_step = "INTAKE_COMPLETED"

        duration = (time.time() - t0) * 1000
        summary_msg = f"Classified document as {doc_type.value} under {jurisdiction}."
        if state.privilege_flag:
            summary_msg += " [PRIVILEGE FLAGGED]"
        if state.deadline_flags:
            summary_msg += f" [{len(state.deadline_flags)} DEADLINE(S) FLAGGED]"

        state.step_traces.append(AgentStepTrace(
            agent_name="IntakeAgent",
            action_summary=summary_msg,
            duration_ms=round(duration, 2),
            details={
                "doc_type": doc_type.value,
                "jurisdiction": jurisdiction,
                "privilege_detected": bool(state.privilege_flag),
                "deadlines_count": len(state.deadline_flags)
            }
        ))
        return state


intake_agent = IntakeAgent()
