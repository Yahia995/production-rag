from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

from app.core.queue import IngestionJobMessage
from app.documents.chunker import DocumentChunk
from app.documents.service import IngestionResult
from workers.ingestion import IngestionWorker


def _worker(dequeue_result):
    queue = MagicMock()
    queue.dequeue.return_value = dequeue_result

    ingestion_service = MagicMock()

    document_id = uuid4()
    chunk = DocumentChunk(
        chunk_id=uuid4(),
        document_id=document_id,
        content="asyncio.TaskGroup manages tasks",
        chunk_index=0,
    )

    parsed_document = MagicMock()
    parsed_document.document_id = document_id

    ingestion_service.ingest.return_value = IngestionResult(
        document=parsed_document,
        chunks=(chunk,),
    )

    embedding_provider = MagicMock()
    embedding_provider.embed_documents.return_value = [[0.1, 0.2]]

    vector_store = MagicMock()

    worker = IngestionWorker(
        queue=queue,
        ingestion_service=ingestion_service,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    return worker, queue, ingestion_service, embedding_provider, vector_store, chunk


def test_process_one_returns_false_when_queue_empty() -> None:
    worker, *_ = _worker(dequeue_result=None)

    assert worker.process_one() is False


def test_process_one_ingests_and_indexes_document() -> None:
    message = IngestionJobMessage(job_id="job-1", source="doc.txt", collection="python")

    worker, queue, ingestion_service, embedding_provider, vector_store, chunk = _worker(
        dequeue_result=message
    )

    processed = worker.process_one()

    assert processed is True
    ingestion_service.ingest.assert_called_once_with(Path("doc.txt"))
    embedding_provider.embed_documents.assert_called_once_with([chunk.content])
    vector_store.ensure_collection.assert_called_once()
    vector_store.upsert.assert_called_once()


def test_process_one_skips_upsert_for_empty_chunks() -> None:
    message = IngestionJobMessage(job_id="job-1", source="doc.txt", collection="python")

    worker, queue, ingestion_service, embedding_provider, vector_store, _ = _worker(
        dequeue_result=message
    )

    ingestion_service.ingest.return_value = IngestionResult(
        document=MagicMock(),
        chunks=(),
    )
    embedding_provider.embed_documents.return_value = []

    worker.process_one()

    vector_store.upsert.assert_not_called()


def test_process_one_reraises_and_logs_on_failure() -> None:
    import pytest

    message = IngestionJobMessage(job_id="job-1", source="doc.txt", collection="python")

    worker, queue, ingestion_service, *_ = _worker(dequeue_result=message)
    ingestion_service.ingest.side_effect = ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        worker.process_one()
