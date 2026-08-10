from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.domain.documents import Document, Clause, DocumentType
from src.domain.findings import Finding
from src.domain.compliance import RulePack
from src.domain.audit import AgentStepTrace

class WorkflowState(BaseModel):
    trace_id: str
    matter_id: str
    document_id: str
    raw_content: str
    filename: str
    document_type: DocumentType = DocumentType.CONTRACT
    jurisdiction: str = "South Africa"
    document_dom: Optional[Document] = None
    clauses: List[Clause] = Field(default_factory=list)
    rule_pack: Optional[RulePack] = None
    research_context: List[Dict[str, Any]] = Field(default_factory=list)
    ai_findings: List[Finding] = Field(default_factory=list)
    deterministic_findings: List[Finding] = Field(default_factory=list)
    final_findings: List[Finding] = Field(default_factory=list)
    human_review_required: bool = False
    step_traces: List[AgentStepTrace] = Field(default_factory=list)
    current_step: str = "INITIATED"
    is_completed: bool = False
