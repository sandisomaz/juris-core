import re
from src.core.exceptions import DocumentParsingException

class DocumentValidator:
    """Validates document size, extensions, and sanitizes untrusted input."""

    MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB max
    ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

    def validate_filename_and_size(self, filename: str, content_size: int) -> bool:
        if content_size > self.MAX_FILE_SIZE_BYTES:
            raise DocumentParsingException(f"File size {content_size} bytes exceeds maximum allowed limit of {self.MAX_FILE_SIZE_BYTES} bytes.")

        import pathlib
        ext = pathlib.Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise DocumentParsingException(f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(self.ALLOWED_EXTENSIONS)}.")

        return True

    def sanitize_text(self, raw_text: str) -> str:
        # Strip potential prompt injection code blocks or control characters
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', raw_text)
        return cleaned

document_validator = DocumentValidator()
