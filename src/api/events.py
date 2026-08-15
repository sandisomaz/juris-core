import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/events", tags=["Events & Streaming"])

async def event_generator():
    sample_events = [
        {"agent": "IntakeAgent", "status": "COMPLETED", "duration_ms": 12.4, "summary": "IntakeAgent: classified 2 matter documents as CONTRACT / DPA"},
        {"agent": "ExtractionAgent", "status": "COMPLETED", "duration_ms": 45.1, "summary": "ExtractionAgent: segmented 5 spatial clause blocks"},
        {"agent": "ResearchAgent", "status": "COMPLETED", "duration_ms": 88.0, "summary": "ResearchAgent: cross-referenced POPIA Act 4 of 2013 §19-22"},
        {"agent": "ComplianceAgent", "status": "COMPLETED", "duration_ms": 62.3, "summary": "ComplianceAgent: evaluated deterministic breach SLA and indemnity caps"},
        {"agent": "VerifierAgent", "status": "COMPLETED", "duration_ms": 34.8, "summary": "VerifierAgent: confirmed 3 citations VALID, 1 WRONG_SECTION"},
        {"agent": "RedlineAgent", "status": "COMPLETED", "duration_ms": 55.2, "summary": "RedlineAgent: generated 2 surgical inline redlines"},
        {"agent": "EscalationAgent", "status": "HUMAN_REVIEW_REQUIRED", "duration_ms": 15.0, "summary": "⚡ EscalationAgent: Human-in-the-Loop review required for Clause 3.0 Breach SLA"}
    ]
    for ev in sample_events:
        yield f"data: {json.dumps(ev)}\n\n"
        await asyncio.sleep(0.5)

@router.get("/stream")
async def stream_agent_events():
    return StreamingResponse(event_generator(), media_type="text/event-stream")
