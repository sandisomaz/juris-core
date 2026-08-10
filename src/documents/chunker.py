import re
from typing import List
from src.domain.documents import Clause

class LegalClauseChunker:
    """Segments raw contract text into structured Clause objects with spatial metadata."""

    # Matches section headings like "1. DEFINITIONS", "SECTION 3. DATA PROTECTION", "Clause 4.2 Liability"
    CLAUSE_PATTERN = re.compile(
        r'^(?P<heading>(?:(?:SECTION|CLAUSE|ARTICLE)\s+)?(?:\d+\.?(?:\d+)?\.?|[A-Z]\.)\s+[A-Z0-9\s,\-\'\"\(\)\:\;\&\/]{3,80})$',
        re.MULTILINE
    )

    def segment_clauses(self, raw_text: str) -> List[Clause]:
        clauses: List[Clause] = []
        paragraphs = raw_text.split("\n\n")

        clause_index = 1
        current_title = "Preamble & Background"
        current_clause_id = "0.0"
        current_buffer = []
        page_num = 1
        para_counter = 1
        char_offset = 0

        for p_idx, para in enumerate(paragraphs):
            para_trimmed = para.strip()
            if not para_trimmed:
                continue

            lines = para_trimmed.split("\n")
            first_line = lines[0].strip()

            # Check if line looks like a section header
            header_match = self.CLAUSE_PATTERN.match(first_line)
            is_header = bool(header_match) or (
                len(first_line) < 80 and
                any(first_line.startswith(prefix) for prefix in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12.", "13.", "14.", "15.", "SECTION", "CLAUSE", "ARTICLE"])
            )

            if is_header and current_buffer:
                # Flush existing buffer as a clause
                body_text = "\n".join(current_buffer)
                clauses.append(Clause(
                    clause_id=current_clause_id,
                    title=current_title,
                    text=body_text,
                    page=page_num,
                    paragraph=para_counter,
                    start_char=char_offset,
                    end_char=char_offset + len(body_text)
                ))
                char_offset += len(body_text) + 2
                current_buffer = []
                clause_index += 1

            if is_header:
                current_title = first_line
                # Extract clause_id from header (e.g., "3.4" or "3")
                id_match = re.search(r'(\d+(?:\.\d+)?)', first_line)
                current_clause_id = id_match.group(1) if id_match else f"{clause_index}.0"
                body_lines = lines[1:]
                if body_lines:
                    current_buffer.append("\n".join(body_lines))
            else:
                current_buffer.append(para_trimmed)

            # Estimate page numbers (~35 lines per page)
            if p_idx > 0 and p_idx % 8 == 0:
                page_num += 1
            para_counter += 1

        # Flush final clause
        if current_buffer:
            body_text = "\n".join(current_buffer)
            clauses.append(Clause(
                clause_id=current_clause_id,
                title=current_title,
                text=body_text,
                page=page_num,
                paragraph=para_counter,
                start_char=char_offset,
                end_char=char_offset + len(body_text)
            ))

        return clauses

legal_clause_chunker = LegalClauseChunker()
