from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_endpoint_is_exposed() -> None:
    response = client.get("/metrics")

    assert response.status_code == 200


def test_metrics_endpoint_contains_rag_metrics() -> None:
    response = client.get("/metrics")

    assert "rag_requests_total" in response.text
    assert "retrieval_latency_seconds" in response.text
