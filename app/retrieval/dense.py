from uuid import UUID

from app.db.qdrant import QdrantVectorStore
from app.embeddings.base import EmbeddingProvider
from app.retrieval.base import RetrievedChunk, Retriever


class DenseRetriever(Retriever):
    """Retriever backed by embedding similarity search in Qdrant."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: QdrantVectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: dict[str, str] | None = None,
    ) -> tuple[RetrievedChunk, ...]:
        query_vector = self.embedding_provider.embed_query(query)

        results = self.vector_store.search(
            vector=query_vector,
            top_k=top_k,
            filters=filters,
        )

        return tuple(self._to_retrieved_chunk(result) for result in results)

    @staticmethod
    def _to_retrieved_chunk(result: dict) -> RetrievedChunk:
        payload = result["payload"]

        return RetrievedChunk(
            chunk_id=UUID(str(result["id"])),
            document_id=UUID(payload["document_id"]),
            content=payload["content"],
            score=result["score"],
            page_number=payload.get("page_number"),
            section=payload.get("section"),
        )
