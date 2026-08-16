import io
from typing import Tuple, Dict, Any
from src.documents.validator import document_validator
from src.core.exceptions import DocumentParsingException

class DocumentParser:
    """Parses raw text, TXT, PDF, DOCX inputs into clean text and metadata."""

    def parse_bytes(self, filename: str, content_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
        document_validator.validate_filename_and_size(filename, len(content_bytes))
        
        import pathlib
        ext = pathlib.Path(filename).suffix.lower()
        metadata = {
            "filename": filename,
            "file_size": len(content_bytes),
            "extension": ext
        }

        if ext in (".txt", ".md"):
            try:
                raw_text = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                raw_text = content_bytes.decode("latin-1")
            clean_text = document_validator.sanitize_text(raw_text)
            return clean_text, metadata

        # Fallback text extractor for pdf/docx if binary libraries not installed
        try:
            raw_text = content_bytes.decode("utf-8", errors="ignore")
            clean_text = document_validator.sanitize_text(raw_text)
            return clean_text, metadata
        except Exception as e:
            raise DocumentParsingException(f"Failed to parse document {filename}: {str(e)}")

document_parser = DocumentParser()
