from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Interface implemented by embedding providers."""

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of documents."""
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimensionality of the embeddings produced."""
        raise NotImplementedError
