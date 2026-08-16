import pytest
from src.agents.supervisor import supervisor_orchestrator
from src.domain.documents import Document, Clause, DocumentType
from src.api.events import _EVENT_HISTORY, broadcast_event


def test_matter_multi_document_workflow():
    doc1 = Document(
        id="doc-msa-01",
        filename="Master_Services_Agreement.txt",
        doc_type=DocumentType.CONTRACT,
        matter_id="mat-multi-01",
        clauses=[
            Clause(
                clause_id="1.0",
                title="Definitions & Security",
                text="Operator agrees to maintain POPIA Section 19 security measures."
            ),
            Clause(
                clause_id="3.0",
                title="Incident Notification Window",
                text="In case of breach, notify Customer within 120 hours of discovery."
            ),
            Clause(
                clause_id="4.0",
                title="Limitation of Liability",
                text="Total aggregate liability shall be capped at 100,000 USD."
            )
        ]
    )

    doc2 = Document(
        id="doc-dpa-02",
        filename="Data_Processing_Addendum.txt",
        doc_type=DocumentType.CONTRACT,
        matter_id="mat-multi-01",
        clauses=[
            Clause(
                clause_id="DPA-2.1",
                title="Breach Notification Protocol",
                text="Operator shall notify Customer without undue delay and within 24 hours of becoming aware of any personal data breach."
            ),
            Clause(
                clause_id="DPA-5.0",
                title="Unlimited Data Protection Indemnity",
                text="Notwithstanding anything in the Principal Agreement, liability for breach of this DPA shall be unlimited."
            )
        ]
    )

    raw_contents = {
        "doc-msa-01": "MSA text with 120 hours notification and 100,000 cap.",
        "doc-dpa-02": "DPA text with 24 hours notification and unlimited liability."
    }

    state, trace = supervisor_orchestrator.run_matter_workflow(
        matter_id="mat-multi-01",
        documents=[doc1, doc2],
        raw_contents=raw_contents
    )

    assert state.is_completed is True
    assert len(trace.steps) >= 7
    assert state.human_review_required is True

    # Verify cross-document findings were flagged
    cross_findings = [f for f in state.final_findings if "Cross-Document" in f.location or f.related_sources]
    assert len(cross_findings) > 0

    # Verify conflicting SLAs or liability carve-outs were caught
    issues = [f.issue for f in state.final_findings]
    assert any("Conflicting" in issue or "Liability" in issue for issue in issues)


@pytest.mark.asyncio
async def test_sse_event_bus_broadcast():
    test_event = {
        "agent": "TestAgent",
        "status": "COMPLETED",
        "duration_ms": 10.5,
        "summary": "Test event broadcast"
    }
    await broadcast_event(test_event)

    assert any(ev.get("agent") == "TestAgent" for ev in _EVENT_HISTORY)
