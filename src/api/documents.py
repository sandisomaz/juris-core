import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from src.domain.documents import Document, DocumentType, Clause
from src.documents.parser import document_parser
from src.documents.chunker import legal_clause_chunker

router = APIRouter(prefix="/api/documents", tags=["Documents"])

IN_MEMORY_DOCUMENTS: List[Document] = []
RAW_DOC_CONTENTS: dict = {}

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
    return doc_obj
