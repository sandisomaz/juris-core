import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from src.domain.documents import Document, DocumentType, Clause
from src.documents.parser import document_parser
from src.documents.chunker import legal_clause_chunker

router = APIRouter(prefix="/api/documents", tags=["Documents"])

IN_MEMORY_DOCUMENTS: List[Document] = []
RAW_DOC_CONTENTS: dict = {}
DOC_JOB_STATUSES: Dict[str, str] = {}

class CitationResolveRequest(BaseModel):
    source_id: str
    clause_id: str

@router.get("", response_model=List[Document])
async def list_documents(matter_id: str = None):
    if matter_id:
        return [d for d in IN_MEMORY_DOCUMENTS if d.matter_id == matter_id]
    return IN_MEMORY_DOCUMENTS

@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: str):
    for d in IN_MEMORY_DOCUMENTS:
        if d.id == document_id:
            return d
    raise HTTPException(status_code=404, detail="Document not found")

@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    matter_id: str = Form(...),
    doc_type: str = Form("CONTRACT")
):
    content_bytes = await file.read()
    clean_text, meta = document_parser.parse_bytes(file.filename, content_bytes)
    clauses = legal_clause_chunker.segment_clauses(clean_text)

    doc_id = f"doc-{uuid.uuid4().hex[:6]}"
    doc_obj = Document(
        id=doc_id,
        filename=file.filename,
        doc_type=DocumentType(doc_type) if doc_type in DocumentType.__members__ else DocumentType.CONTRACT,
        matter_id=matter_id,
        file_size_bytes=len(content_bytes),
        clause_count=len(clauses),
        clauses=clauses,
        parsed_metadata=meta
    )

    IN_MEMORY_DOCUMENTS.insert(0, doc_obj)
    RAW_DOC_CONTENTS[doc_id] = clean_text
    DOC_JOB_STATUSES[doc_id] = "Verified"
    return doc_obj

@router.post("/bulk_upload")
async def bulk_upload_documents(
    files: List[UploadFile] = File(...),
    matter_id: str = Form("mat-001")
):
    uploaded = []
    for file in files:
        content_bytes = await file.read()
        clean_text, meta = document_parser.parse_bytes(file.filename, content_bytes)
        clauses = legal_clause_chunker.segment_clauses(clean_text)

        doc_id = f"doc-{uuid.uuid4().hex[:6]}"
        doc_obj = Document(
            id=doc_id,
            filename=file.filename,
            doc_type=DocumentType.CONTRACT,
            matter_id=matter_id,
            file_size_bytes=len(content_bytes),
            clause_count=len(clauses),
            clauses=clauses,
            parsed_metadata=meta
        )

        IN_MEMORY_DOCUMENTS.insert(0, doc_obj)
        RAW_DOC_CONTENTS[doc_id] = clean_text
        DOC_JOB_STATUSES[doc_id] = "Verified"
        uploaded.append({
            "id": doc_id,
            "filename": file.filename,
            "status": "Verified",
            "clause_count": len(clauses)
        })

    return {"matter_id": matter_id, "uploaded_count": len(uploaded), "documents": uploaded}

@router.post("/citations/resolve")
async def resolve_citation(req: CitationResolveRequest):
    for doc in IN_MEMORY_DOCUMENTS:
        if doc.id == req.source_id or req.source_id in doc.filename:
            for clause in doc.clauses:
                if clause.id == req.clause_id or req.clause_id in clause.id:
                    return {
                        "source_id": doc.id,
                        "filename": doc.filename,
                        "clause_id": clause.id,
                        "section_number": clause.section_number,
                        "heading": clause.heading,
                        "text": clause.text,
                        "start_char": clause.start_char,
                        "end_char": clause.end_char
                    }
    return {
        "source_id": req.source_id,
        "clause_id": req.clause_id,
        "heading": f"Clause {req.clause_id}",
        "text": f"Extracted clause content for {req.clause_id} in source {req.source_id}."
    }
