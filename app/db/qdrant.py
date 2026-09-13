from dataclasses import dataclass
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import get_settings


@dataclass(frozen=True, slots=True)
class VectorRecord:
    chunk_id: UUID
    document_id: UUID
    vector: list[float]
    content: str
    page_number: int | None = None
    section: str | None = None
    metadata: dict[str, str] | None = None


class QdrantVectorStore:
    """Thin wrapper around the Qdrant client for chunk-level vector storage."""

    def __init__(
        self,
        collection_name: str,
        vector_size: int,
        client: QdrantClient | None = None,
    ) -> None:
        settings = get_settings()

        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = client or QdrantClient(url=settings.qdrant_url)

    def ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE,
            ),
        )

    def upsert(self, records: list[VectorRecord]) -> None:
        points = [
            PointStruct(
                id=str(record.chunk_id),
                vector=record.vector,
                payload={
                    "document_id": str(record.document_id),
                    "content": record.content,
                    "page_number": record.page_number,
                    "section": record.section,
                    **(record.metadata or {}),
                },
            )
            for record in records
        ]

        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self,
        vector: list[float],
        top_k: int = 10,
        filters: dict[str, str] | None = None,
    ) -> list[dict]:
        query_filter = self._build_filter(filters)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k,
            query_filter=query_filter,
        )

        return [
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload,
            }
            for point in results.points
        ]

    def delete_document(self, document_id: UUID) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=str(document_id)),
                    )
                ]
            ),
        )

    @staticmethod
    def _build_filter(filters: dict[str, str] | None) -> Filter | None:
        if not filters:
            return None

        return Filter(
            must=[
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in filters.items()
            ]
        )
