import pytest
from uuid import uuid4

from app.retrieval.base import RetrievedChunk
from app.reranking.base import Reranker


def test_reranker_is_abstract() -> None:
    with pytest.raises(TypeError):
        Reranker()  # type: ignore[abstract]


def test_reranker_requires_rerank_implementation() -> None:
    class IncompleteReranker(Reranker):
        pass

    with pytest.raises(TypeError):
        IncompleteReranker()  # type: ignore[abstract]


def test_reranker_implementation_can_be_used() -> None:
    class TestReranker(Reranker):
        def rerank(
            self,
            query: str,
            chunks: tuple[RetrievedChunk, ...],
            top_n: int = 5,
        ) -> tuple[RetrievedChunk, ...]:
            return chunks[:top_n]

    chunk = RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content="hello",
        score=0.5,
    )

    reranker = TestReranker()

    assert isinstance(reranker, Reranker)
    assert reranker.rerank("query", (chunk,)) == (chunk,)
