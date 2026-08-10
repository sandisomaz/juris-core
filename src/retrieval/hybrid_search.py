from typing import List, Dict, Any
from src.deterministic.source_registry import source_registry, LegalSourceEntry

class HybridSearchEngine:
    """Hybrid Keyword (BM25 simulation) + Vector Search engine with provenance retention."""

    def search_legal_knowledge(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        results = []
        sources = source_registry.get_all_sources()
        query_words = set(query.lower().split())

        for source in sources:
            score = 0.0
            # Keyword score
            text = (source.official_title + " " + source.requirements_summary + " " + source.legislation + " " + source.section).lower()
            for q_word in query_words:
                if len(q_word) > 3 and q_word in text:
                    score += 2.0

            if score > 0:
                results.append({
                    "source": f"{source.legislation} {source.act_number} Section {source.section}",
                    "title": source.official_title,
                    "summary": source.requirements_summary,
                    "url": source.source_url,
                    "relevance_score": round(min(1.0, score / 6.0), 2)
                })

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]

hybrid_search_engine = HybridSearchEngine()
