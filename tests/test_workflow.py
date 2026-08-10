from src.agents.supervisor import supervisor_orchestrator

def test_full_agent_workflow():
    content = """MASTER AGREEMENT
1. SECURITY MEASURES
Operator agrees to maintain POPIA Section 19 security measures.

2. BREACH NOTIFICATION
In case of breach, notify Customer within 120 hours.
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
