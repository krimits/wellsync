"""
WellnessRetriever — RAG layer for evidence-based recommendations.

Retrieves relevant wellness guidelines from the knowledge_chunks table
using pgvector cosine similarity search.

Dependencies:
    pip install sentence-transformers pgvector
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer


# Loaded once at module import — model is ~90MB, cached on disk after first download
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model (singleton per process)."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


class WellnessRetriever:
    """
    Retrieves top-k relevant wellness knowledge chunks for a given query.

    Usage:
        retriever = WellnessRetriever(db)
        docs = retriever.retrieve("sleep 6h quality 3/5 stress 4/5 readiness 58", k=2)
        # docs → list of 2 wellness guideline strings
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.model = _get_model()

    def retrieve(self, query: str, k: int = 2) -> list[str]:
        """
        Return top-k relevant wellness knowledge chunks for query.

        Args:
            query: Free-text description of user's current state
                   (e.g. "sleep 6h quality 3/5 stress 4/5 readiness 58")
            k:     Number of chunks to retrieve (default: 2 to stay within token budget)

        Returns:
            List of guideline strings, ordered by relevance (most relevant first).
            Returns [] if the knowledge_chunks table is empty or an error occurs.
        """
        try:
            embedding: list[float] = self.model.encode(query).tolist()
            # pgvector <-> operator = cosine distance (lower = more similar)
            rows = self.db.execute(
                """
                SELECT content
                FROM knowledge_chunks
                ORDER BY embedding <-> CAST(:emb AS vector)
                LIMIT :k
                """,
                {"emb": str(embedding), "k": k},
            ).fetchall()
            return [row[0] for row in rows]
        except Exception:
            # Graceful degradation: if RAG fails, agent proceeds without guidelines
            return []
