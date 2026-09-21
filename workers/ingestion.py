import logging
from pathlib import Path
from uuid import UUID

from app.core.queue import IngestionJobMessage, RedisJobQueue
from app.db.qdrant import QdrantVectorStore, VectorRecord
from app.documents.service import DocumentIngestionService
from app.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)


class IngestionWorker:
    """Consumes ingestion jobs and runs them through the ingestion pipeline."""

    def __init__(
        self,
        queue: RedisJobQueue,
        ingestion_service: DocumentIngestionService,
        embedding_provider: EmbeddingProvider,
        vector_store: QdrantVectorStore,
    ) -> None:
        self.queue = queue
        self.ingestion_service = ingestion_service
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def process_one(self, timeout: int = 0) -> bool:
        message = self.queue.dequeue(timeout=timeout)

        if message is None:
            return False

        self._process(message)

        return True

    def _process(self, message: IngestionJobMessage) -> None:
        try:
            self._ingest(message)
        except Exception:
            logger.exception("ingestion job failed", extra={"job_id": message.job_id})
            raise

    def _ingest(self, message: IngestionJobMessage) -> None:
        result = self.ingestion_service.ingest(Path(message.source))

        contents = [chunk.content for chunk in result.chunks]
        vectors = self.embedding_provider.embed_documents(contents)

        self.vector_store.ensure_collection()

        records = [
            VectorRecord(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                vector=vector,
                content=chunk.content,
                page_number=chunk.page_number,
                section=chunk.section,
                metadata={"collection": message.collection},
            )
            for chunk, vector in zip(result.chunks, vectors, strict=True)
        ]

        if records:
            self.vector_store.upsert(records)

        logger.info(
            "ingestion job completed",
            extra={"job_id": message.job_id, "chunk_count": len(records)},
        )
