from abc import ABC, abstractmethod

from app.retrieval.base import RetrievedChunk


class Reranker(ABC):
    """Interface implemented by rerankers."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        chunks: tuple[RetrievedChunk, ...],
        top_n: int = 5,
    ) -> tuple[RetrievedChunk, ...]:
        """Rerank candidate chunks against the query."""
        raise NotImplementedError
