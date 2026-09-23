from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_db, get_ingestion_queue, get_vector_store
from app.main import app

client = TestClient(app)


def _override_queue():
    queue = MagicMock()
    app.dependency_overrides[get_ingestion_queue] = lambda: queue

    return queue


def _document(document_id):
    document = MagicMock()
    document.id = document_id
    document.source = "docs/asyncio.md"
    document.title = "Asyncio"
    document.document_type = "markdown"
    document.collection = "python"
    document.created_at = datetime.now(UTC)
    document.updated_at = datetime.now(UTC)

    return document


def test_create_document_enqueues_job() -> None:
    queue = _override_queue()

    response = client.post(
        "/documents",
        json={"source": "docs/asyncio.md", "collection": "python"},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["source"] == "docs/asyncio.md"
    assert body["collection"] == "python"
    assert body["status"] == "pending"
    queue.enqueue.assert_called_once()

    app.dependency_overrides.clear()


def test_create_document_defaults_collection() -> None:
    _override_queue()

    response = client.post("/documents", json={"source": "docs/asyncio.md"})

    assert response.json()["collection"] == "default"

    app.dependency_overrides.clear()


def test_create_document_rejects_missing_source() -> None:
    _override_queue()

    response = client.post("/documents", json={})

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_create_documents_batch_enqueues_all() -> None:
    queue = _override_queue()

    response = client.post(
        "/documents/batch",
        json=[
            {"source": "a.md", "collection": "python"},
            {"source": "b.md", "collection": "python"},
        ],
    )

    assert response.status_code == 202
    assert len(response.json()) == 2
    assert queue.enqueue.call_count == 2

    app.dependency_overrides.clear()


def test_create_documents_batch_rejects_empty_list() -> None:
    _override_queue()

    response = client.post("/documents/batch", json=[])

    assert response.status_code == 400

    app.dependency_overrides.clear()


def test_list_documents_returns_documents() -> None:
    session = MagicMock()
    document_id = uuid4()

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "app.documents.repository.DocumentRepository.list_documents",
        return_value=[_document(document_id)],
    ):
        app.dependency_overrides[get_db] = lambda: session

        response = client.get("/documents")

        assert response.status_code == 200
        assert len(response.json()) == 1

        app.dependency_overrides.clear()


def test_get_document_returns_404_when_missing() -> None:
    session = MagicMock()

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "app.documents.repository.DocumentRepository.get_document",
        return_value=None,
    ):
        app.dependency_overrides[get_db] = lambda: session

        response = client.get(f"/documents/{uuid4()}")

        assert response.status_code == 404

        app.dependency_overrides.clear()


def test_delete_document_removes_from_vector_store() -> None:
    session = MagicMock()
    document_id = uuid4()
    vector_store = MagicMock()

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "app.documents.repository.DocumentRepository.delete_document",
        return_value=True,
    ):
        app.dependency_overrides[get_db] = lambda: session
        app.dependency_overrides[get_vector_store] = lambda: vector_store

        response = client.delete(f"/documents/{document_id}")

        assert response.status_code == 204
        vector_store.delete_document.assert_called_once_with(document_id)

        app.dependency_overrides.clear()


def test_delete_document_returns_404_when_missing() -> None:
    session = MagicMock()

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "app.documents.repository.DocumentRepository.delete_document",
        return_value=False,
    ):
        app.dependency_overrides[get_db] = lambda: session

        response = client.delete(f"/documents/{uuid4()}")

        assert response.status_code == 404

        app.dependency_overrides.clear()
