from typing import List, Optional
from fastapi import APIRouter
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
    # Return mock trace if none exists
    return AgentRunTrace(
        trace_id=trace_id,
        matter_id="mat-001",
        document_id="doc-001",
        total_duration_ms=420.5,
        steps=[]
    )
