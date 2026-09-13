import math

from app.embeddings.local import LocalEmbeddingProvider


def test_local_provider_returns_configured_dimension() -> None:
    provider = LocalEmbeddingProvider(dimension=64)

    vector = provider.embed_query("connection pooling")

    assert len(vector) == 64
    assert provider.dimension == 64


def test_local_provider_is_deterministic() -> None:
    provider = LocalEmbeddingProvider()

    first = provider.embed_query("asyncio.TaskGroup")
    second = provider.embed_query("asyncio.TaskGroup")

    assert first == second


def test_local_provider_embeds_document_batches() -> None:
    provider = LocalEmbeddingProvider()

    vectors = provider.embed_documents(["hello world", "goodbye world"])

    assert len(vectors) == 2
    assert len(vectors[0]) == provider.dimension


def test_local_provider_returns_unit_vectors() -> None:
    provider = LocalEmbeddingProvider()

    vector = provider.embed_query("normalize this text")
    norm = math.sqrt(sum(value * value for value in vector))

    assert math.isclose(norm, 1.0, rel_tol=1e-6)


def test_local_provider_handles_empty_text() -> None:
    provider = LocalEmbeddingProvider()

    vector = provider.embed_query("")

    assert vector == [0.0] * provider.dimension


def test_local_provider_rejects_non_positive_dimension() -> None:
    import pytest

    with pytest.raises(ValueError, match="dimension"):
        LocalEmbeddingProvider(dimension=0)
