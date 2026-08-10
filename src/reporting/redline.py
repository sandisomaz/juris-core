import difflib
from typing import Dict, Any

class RedlineDiffGenerator:
    """Generates inline HTML / Markdown redline diffs for legal review."""

    def generate_html_diff(self, original_text: str, proposed_text: str) -> str:
        orig_words = original_text.split()
        prop_words = proposed_text.split()

        matcher = difflib.SequenceMatcher(None, orig_words, prop_words)
        output = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                output.append(" ".join(orig_words[i1:i2]))
            elif tag == 'delete':
                deleted_str = " ".join(orig_words[i1:i2])
                output.append(f'<del style="background-color: #ffebe9; color: #cf222e; text-decoration: line-through; padding: 2px 4px; border-radius: 3px;">{deleted_str}</del>')
            elif tag == 'insert':
                inserted_str = " ".join(prop_words[j1:j2])
                output.append(f'<ins style="background-color: #dafbe1; color: #1a7f37; text-decoration: none; font-weight: 600; padding: 2px 4px; border-radius: 3px;">{inserted_str}</ins>')
            elif tag == 'replace':
                deleted_str = " ".join(orig_words[i1:i2])
                inserted_str = " ".join(prop_words[j1:j2])
                output.append(f'<del style="background-color: #ffebe9; color: #cf222e; text-decoration: line-through; padding: 2px 4px; border-radius: 3px;">{deleted_str}</del> <ins style="background-color: #dafbe1; color: #1a7f37; text-decoration: none; font-weight: 600; padding: 2px 4px; border-radius: 3px;">{inserted_str}</ins>')

        return " ".join(output)

redline_diff_generator = RedlineDiffGenerator()
