from typing import List, Dict, Any
from src.retrieval.hybrid_search import hybrid_search_engine

class LegalSourceProvider:
    def get_context_for_clause(self, clause_title: str, clause_text: str) -> List[Dict[str, Any]]:
        query = f"{clause_title} {clause_text[:200]}"
        return hybrid_search_engine.search_legal_knowledge(query, top_k=2)

legal_source_provider = LegalSourceProvider()
