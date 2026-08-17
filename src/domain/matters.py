from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class MatterRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class MatterStatus(str, Enum):
    ACTIVE = "ACTIVE"
    UNDER_REVIEW = "UNDER_REVIEW"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class MatterBase(BaseModel):
    title: str = Field(..., description="Title of the legal matter")
    client_name: str = Field(..., description="Client or business department name")
    jurisdiction: str = Field("South Africa", description="Governing legal jurisdiction")
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class MatterCreate(MatterBase):
    pass

class Matter(MatterBase):
    id: str
    status: MatterStatus = MatterStatus.ACTIVE
    overall_risk: MatterRiskLevel = MatterRiskLevel.LOW
    document_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
