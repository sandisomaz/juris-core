from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class AuditEvent(BaseModel):
    event_id: str
    matter_id: str
    document_id: Optional[str] = None
    finding_id: Optional[str] = None
    action: str = Field(..., description="Action taken, e.g. HUMAN_APPROVAL, REDLINE_ACCEPTED, REVIEW_STARTED")
    actor: str = Field(..., description="User ID or Agent Name")
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AgentStepTrace(BaseModel):
    agent_name: str
    action_summary: str
    status: str = "SUCCESS"
    duration_ms: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = Field(default_factory=dict)

class AgentRunTrace(BaseModel):
    trace_id: str
    matter_id: str
    document_id: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0.0
    steps: List[AgentStepTrace] = Field(default_factory=list)
