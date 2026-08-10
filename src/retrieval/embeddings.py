from typing import List

class EmbeddingsGenerator:
    """Mockable / Swappable Embeddings Generator."""

    def generate_embedding(self, text: str) -> List[float]:
        # Simple deterministic hash-based vector generator for fast offline retrieval
        vector = [0.0] * 64
        for idx, char in enumerate(text[:64]):
            vector[idx % 64] += (ord(char) % 10) / 10.0
        return vector

embeddings_generator = EmbeddingsGenerator()
