from src.agents.supervisor import supervisor_orchestrator
from src.deterministic.privilege_detector import detect_privilege
from src.deterministic.deadline_detector import detect_deadlines


def test_full_agent_workflow():
    content = """MASTER AGREEMENT
CONFIDENTIAL & PRIVILEGED ATTORNEY-CLIENT COMMUNICATION

1. SECURITY MEASURES
Operator agrees to maintain POPIA Section 19 security measures.

2. BREACH NOTIFICATION
In case of breach, notify Customer within 120 hours of discovery.
"""
    state, trace = supervisor_orchestrator.run_workflow(
        matter_id="mat-test",
        document_id="doc-test",
        filename="test_contract.txt",
        content=content
    )

    assert state.is_completed is True
    assert len(trace.steps) >= 6
    assert state.human_review_required is True
    assert state.privilege_flag is not None
    assert len(state.deadline_flags) > 0


def test_privilege_detector_direct():
    text = "WITHOUT PREJUDICE. Settlement proposal between attorney and client."
    flag = detect_privilege(text)
    assert flag is not None
    assert any("without prejudice" in t for t in flag["matched_terms"])


def test_deadline_detector_direct():
    text = "Response must be filed within 10 business days on or before 15 October 2026."
    deadlines = detect_deadlines(text)
    assert len(deadlines) > 0
