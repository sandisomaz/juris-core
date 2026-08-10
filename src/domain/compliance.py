from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RuleCategory(str, Enum):
    MANDATORY_CLAUSE = "MANDATORY_CLAUSE"
    STATUTORY_CITATION = "STATUTORY_CITATION"
    TIMEFRAME_SLA = "TIMEFRAME_SLA"
    NUMERICAL_THRESHOLD = "NUMERICAL_THRESHOLD"
    REQUIRED_DISCLOSURE = "REQUIRED_DISCLOSURE"
    POLICY_COMPLIANCE = "POLICY_COMPLIANCE"

class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class RuleRequirement(BaseModel):
    rule_id: str = Field(..., description="E.g. POPIA-017")
    title: str
    category: RuleCategory
    severity: SeverityLevel
    description: str
    mandatory_keywords: List[str] = Field(default_factory=list)
    prohibited_keywords: List[str] = Field(default_factory=list)
    statutory_reference: Optional[str] = None
    min_timeframe_hours: Optional[int] = None
    max_timeframe_hours: Optional[int] = None

class RulePack(BaseModel):
    pack_id: str
    name: str = Field(..., description="E.g. POPIA Compliance Pack v1.0")
    jurisdiction: str = "South Africa"
    description: str
    rules: List[RuleRequirement] = Field(default_factory=list)
