from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies import get_rag_pipeline
from app.main import app
from app.rag.citation import Citation
from app.rag.pipeline import RagAnswer

client = TestClient(app)


def _override_pipeline(answer_text: str, citations=()):
    pipeline = MagicMock()
    pipeline.answer.return_value = RagAnswer(text=answer_text, citations=citations)

    app.dependency_overrides[get_rag_pipeline] = lambda: pipeline

    return pipeline


def test_chat_endpoint_returns_answer() -> None:
    _override_pipeline("Connection pooling reuses connections.")

    response = client.post("/chat", json={"question": "What is connection pooling?"})

    assert response.status_code == 200
    assert response.json()["answer"] == "Connection pooling reuses connections."

    app.dependency_overrides.clear()


def test_chat_endpoint_returns_citations() -> None:
    citation = Citation(
        index=1,
        document_id="doc-1",
        chunk_id="chunk-1",
        content="pooling reuses connections",
    )

    _override_pipeline("Answer [1].", citations=(citation,))

    response = client.post("/chat", json={"question": "What is pooling?"})

    body = response.json()
    assert len(body["citations"]) == 1
    assert body["citations"][0]["document_id"] == "doc-1"

    app.dependency_overrides.clear()


def test_chat_endpoint_passes_history_to_pipeline() -> None:
    pipeline = _override_pipeline("answer")

    client.post(
        "/chat",
        json={
            "question": "How do I configure it?",
            "history": [
                {"role": "user", "content": "What is connection pooling?"},
                {"role": "assistant", "content": "It reuses connections."},
            ],
        },
    )

    _, kwargs = pipeline.answer.call_args
    assert len(kwargs["history"]) == 2

    app.dependency_overrides.clear()


def test_chat_endpoint_passes_filters_to_pipeline() -> None:
    pipeline = _override_pipeline("answer")

    client.post(
        "/chat",
        json={"question": "question", "filters": {"collection": "python"}},
    )

    _, kwargs = pipeline.answer.call_args
    assert kwargs["filters"] == {"collection": "python"}

    app.dependency_overrides.clear()


def test_chat_endpoint_rejects_missing_question() -> None:
    response = client.post("/chat", json={})

    assert response.status_code == 422
