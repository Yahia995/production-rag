from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies import get_ingestion_queue
from app.main import app

client = TestClient(app)


def _override_queue():
    queue = MagicMock()
    app.dependency_overrides[get_ingestion_queue] = lambda: queue

    return queue


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
