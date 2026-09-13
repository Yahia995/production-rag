from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_id: UUID
    document_id: UUID
    content: str
    score: float
    page_number: int | None = None
    section: str | None = None


class Retriever(ABC):
    """Interface implemented by retrieval backends."""

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: dict[str, str] | None = None,
    ) -> tuple[RetrievedChunk, ...]:
        """Retrieve the most relevant chunks for a query."""
        raise NotImplementedError
