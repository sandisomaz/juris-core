import asyncio
import json
import time
from typing import Dict, Any, List, AsyncGenerator
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/events", tags=["Events & Streaming"])

# Global event bus subscriber queues
_EVENT_SUBSCRIBERS: List[asyncio.Queue] = []
_EVENT_HISTORY: List[Dict[str, Any]] = [
    {"agent": "IntakeAgent", "status": "COMPLETED", "duration_ms": 12.4, "summary": "IntakeAgent: classified 2 matter documents as CONTRACT / DPA", "timestamp": time.time()},
    {"agent": "ExtractionAgent", "status": "COMPLETED", "duration_ms": 45.1, "summary": "ExtractionAgent: segmented spatial clause blocks", "timestamp": time.time()},
    {"agent": "ResearchAgent", "status": "COMPLETED", "duration_ms": 88.0, "summary": "ResearchAgent: cross-referenced POPIA Act 4 of 2013 s19-22", "timestamp": time.time()},
    {"agent": "ComplianceAgent", "status": "COMPLETED", "duration_ms": 62.3, "summary": "ComplianceAgent: evaluated deterministic breach SLA and indemnity caps", "timestamp": time.time()},
    {"agent": "VerifierAgent", "status": "COMPLETED", "duration_ms": 34.8, "summary": "VerifierAgent: confirmed citations VALID, flagged WRONG_SECTION", "timestamp": time.time()},
    {"agent": "RedlineAgent", "status": "COMPLETED", "duration_ms": 55.2, "summary": "RedlineAgent: generated surgical inline redlines", "timestamp": time.time()},
    {"agent": "EscalationAgent", "status": "HUMAN_REVIEW_REQUIRED", "duration_ms": 15.0, "summary": "EscalationAgent: Human-in-the-Loop review required for Clause 3.0 Breach SLA", "timestamp": time.time()}
]


async def broadcast_event(event_data: Dict[str, Any]):
    """Broadcasts a new agent event to all active SSE subscribers."""
    event_data["timestamp"] = time.time()
    _EVENT_HISTORY.append(event_data)
    if len(_EVENT_HISTORY) > 100:
        _EVENT_HISTORY.pop(0)

    for queue in list(_EVENT_SUBSCRIBERS):
        try:
            queue.put_nowait(event_data)
        except Exception:
            pass


def sync_broadcast_event(event_data: Dict[str, Any]):
    """Synchronous helper to broadcast events into active subscriber queues."""
    event_data["timestamp"] = time.time()
    _EVENT_HISTORY.append(event_data)
    if len(_EVENT_HISTORY) > 100:
        _EVENT_HISTORY.pop(0)

    for queue in list(_EVENT_SUBSCRIBERS):
        try:
            queue.put_nowait(event_data)
        except Exception:
            pass


async def sse_event_generator(request: Request) -> AsyncGenerator[str, None]:
    queue = asyncio.Queue()
    _EVENT_SUBSCRIBERS.append(queue)

    try:
        # Replay recent history on initial connect
        for ev in _EVENT_HISTORY[-5:]:
            yield f"data: {json.dumps(ev)}\n\n"

        while True:
            if await request.is_disconnected():
                break

            try:
                # Wait for next live broadcast event with a 15-second heartbeat
                ev = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield f"data: {json.dumps(ev)}\n\n"
            except asyncio.TimeoutError:
                # Send SSE keep-alive heartbeat comment
                yield ": keep-alive\n\n"
    finally:
        if queue in _EVENT_SUBSCRIBERS:
            _EVENT_SUBSCRIBERS.remove(queue)


@router.get("/stream")
async def stream_agent_events(request: Request):
    return StreamingResponse(
        sse_event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_event_history():
    return _EVENT_HISTORY
