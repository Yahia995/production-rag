from uuid import uuid4

import pytest

from app.retrieval.base import RetrievedChunk, Retriever


def test_retriever_is_abstract() -> None:
    with pytest.raises(TypeError):
        Retriever()  # type: ignore[abstract]


def test_retriever_requires_retrieve_implementation() -> None:
    class IncompleteRetriever(Retriever):
        pass

    with pytest.raises(TypeError):
        IncompleteRetriever()  # type: ignore[abstract]


def test_retriever_implementation_can_be_used() -> None:
    class TestRetriever(Retriever):
        def retrieve(
            self,
            query: str,
            top_k: int = 10,
            filters: dict[str, str] | None = None,
        ) -> tuple[RetrievedChunk, ...]:
            return ()

    retriever = TestRetriever()

    assert isinstance(retriever, Retriever)
    assert retriever.retrieve("test") == ()


def test_retrieved_chunk_is_immutable() -> None:
    chunk = RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content="hello",
        score=0.9,
    )

    with pytest.raises(AttributeError):
        chunk.score = 0.1  # type: ignore[misc]
