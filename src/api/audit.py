import json
from typing import List, Optional
from fastapi import APIRouter, Response
from src.domain.audit import AuditEvent, AgentRunTrace
from src.api.reviews import IN_MEMORY_AUDIT_LOGS, IN_MEMORY_TRACES

router = APIRouter(prefix="/api/audit", tags=["Audit & Observability"])

@router.get("/events", response_model=List[AuditEvent])
async def list_audit_events():
    return IN_MEMORY_AUDIT_LOGS

@router.get("/traces/{trace_id}", response_model=AgentRunTrace)
async def get_agent_trace(trace_id: str):
    trace = IN_MEMORY_TRACES.get(trace_id)
    if trace:
        return trace
    return AgentRunTrace(
        trace_id=trace_id,
        matter_id="mat-001",
        document_id="doc-001",
        total_duration_ms=420.5,
        steps=[]
    )

@router.get("/export")
async def export_audit_trail():
    export_payload = {
        "platform": "JurisCore",
        "export_timestamp": "2026-08-15T18:00:00Z",
        "total_events": len(IN_MEMORY_AUDIT_LOGS),
        "events": [e.dict() for e in IN_MEMORY_AUDIT_LOGS]
    }
    content = json.dumps(export_payload, indent=2, default=str)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=juriscore_audit_trail.json"}
    )
