from uuid import uuid4

from app.db.qdrant import QdrantVectorStore, VectorRecord


def _store(qdrant_client) -> QdrantVectorStore:
    return QdrantVectorStore(
        collection_name="integration_test_chunks",
        vector_size=4,
        client=qdrant_client,
    )


def test_ensure_collection_creates_collection(qdrant_client) -> None:
    store = _store(qdrant_client)
    store.ensure_collection()

    assert qdrant_client.collection_exists("integration_test_chunks")

    qdrant_client.delete_collection("integration_test_chunks")


def test_upsert_and_search_returns_nearest_vector(qdrant_client) -> None:
    store = _store(qdrant_client)
    store.ensure_collection()

    document_id = uuid4()
    chunk_id = uuid4()

    store.upsert(
        [
            VectorRecord(
                chunk_id=chunk_id,
                document_id=document_id,
                vector=[1.0, 0.0, 0.0, 0.0],
                content="asyncio.TaskGroup manages tasks",
            )
        ]
    )

    results = store.search(vector=[1.0, 0.0, 0.0, 0.0], top_k=1)

    assert len(results) == 1
    assert results[0]["payload"]["document_id"] == str(document_id)

    qdrant_client.delete_collection("integration_test_chunks")


def test_delete_document_removes_points(qdrant_client) -> None:
    store = _store(qdrant_client)
    store.ensure_collection()

    document_id = uuid4()

    store.upsert(
        [
            VectorRecord(
                chunk_id=uuid4(),
                document_id=document_id,
                vector=[0.5, 0.5, 0.0, 0.0],
                content="content to delete",
            )
        ]
    )

    store.delete_document(document_id)

    results = store.search(vector=[0.5, 0.5, 0.0, 0.0], top_k=5)

    assert all(r["payload"]["document_id"] != str(document_id) for r in results)

    qdrant_client.delete_collection("integration_test_chunks")
