from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    CONTRACT = "CONTRACT"
    POLICY = "POLICY"
    ONBOARDING_PACK = "ONBOARDING_PACK"
    SUPPLIER_FORM = "SUPPLIER_FORM"
    PROCEDURE = "PROCEDURE"
    MEMO = "MEMO"
    COURT_FILING = "COURT_FILING"
    NOTICE = "NOTICE"
    INVOICE = "INVOICE"
    UNKNOWN = "UNKNOWN"

class Clause(BaseModel):
    clause_id: str = Field(..., description="Unique clause section reference, e.g. 3.4")
    title: str = Field(..., description="Clause heading or title")
    text: str = Field(..., description="Full raw clause text")
    page: int = Field(1, description="Page number where clause starts")
    paragraph: int = Field(1, description="Paragraph index within document")
    start_char: int = Field(0, description="Start character offset")
    end_char: int = Field(0, description="End character offset")
    subclauses: List[str] = Field(default_factory=list, description="Subclause identifiers")

class DocumentBase(BaseModel):
    filename: str
    doc_type: DocumentType = DocumentType.CONTRACT
    matter_id: str
    file_size_bytes: int = 0

class DocumentCreate(DocumentBase):
    content_raw: str

class Document(DocumentBase):
    id: str
    version: int = 1
    upload_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    clause_count: int = 0
    processing_status: str = "Verified"
    clauses: List[Clause] = Field(default_factory=list)
    parsed_metadata: Dict[str, Any] = Field(default_factory=dict)
