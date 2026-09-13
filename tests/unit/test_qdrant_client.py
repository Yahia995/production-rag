from unittest.mock import MagicMock
from uuid import uuid4

from app.db.qdrant import QdrantVectorStore, VectorRecord


def _store(client: MagicMock) -> QdrantVectorStore:
    return QdrantVectorStore(
        collection_name="test_collection",
        vector_size=4,
        client=client,
    )


def test_ensure_collection_creates_when_missing() -> None:
    client = MagicMock()
    client.collection_exists.return_value = False

    store = _store(client)
    store.ensure_collection()

    client.create_collection.assert_called_once()


def test_ensure_collection_skips_when_present() -> None:
    client = MagicMock()
    client.collection_exists.return_value = True

    store = _store(client)
    store.ensure_collection()

    client.create_collection.assert_not_called()


def test_upsert_sends_points() -> None:
    client = MagicMock()
    store = _store(client)

    document_id = uuid4()
    record = VectorRecord(
        chunk_id=uuid4(),
        document_id=document_id,
        vector=[0.1, 0.2, 0.3, 0.4],
        content="hello",
    )

    store.upsert([record])

    client.upsert.assert_called_once()
    _, kwargs = client.upsert.call_args
    assert kwargs["collection_name"] == "test_collection"
    assert kwargs["points"][0].payload["document_id"] == str(document_id)


def test_delete_document_filters_by_document_id() -> None:
    client = MagicMock()
    store = _store(client)
    document_id = uuid4()

    store.delete_document(document_id)

    client.delete.assert_called_once()
    _, kwargs = client.delete.call_args
    assert kwargs["collection_name"] == "test_collection"
