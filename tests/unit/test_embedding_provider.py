import pytest

from app.embeddings.base import EmbeddingProvider


def test_embedding_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        EmbeddingProvider()  # type: ignore[abstract]


def test_embedding_provider_requires_full_implementation() -> None:
    class IncompleteProvider(EmbeddingProvider):
        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            raise NotImplementedError

    with pytest.raises(TypeError):
        IncompleteProvider()  # type: ignore[abstract]


def test_embedding_provider_implementation_can_be_used() -> None:
    class TestProvider(EmbeddingProvider):
        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.0] for _ in texts]

        def embed_query(self, text: str) -> list[float]:
            return [0.0]

        @property
        def dimension(self) -> int:
            return 1

    provider = TestProvider()

    assert isinstance(provider, EmbeddingProvider)
    assert provider.dimension == 1
