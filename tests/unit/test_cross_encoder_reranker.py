from unittest.mock import MagicMock
from uuid import uuid4

from app.retrieval.base import RetrievedChunk
from app.reranking.cross_encoder import CrossEncoderReranker


def _chunk(content: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content=content,
        score=0.0,
    )


def test_reranker_orders_chunks_by_model_score() -> None:
    model = MagicMock()
    model.predict.return_value = [0.2, 0.9, 0.5]

    chunks = (_chunk("low"), _chunk("high"), _chunk("mid"))

    reranker = CrossEncoderReranker(model_name="test-model", model=model)
    results = reranker.rerank("query", chunks)

    assert [chunk.content for chunk in results] == ["high", "mid", "low"]


def test_reranker_respects_top_n() -> None:
    model = MagicMock()
    model.predict.return_value = [0.1, 0.9, 0.5]

    chunks = (_chunk("a"), _chunk("b"), _chunk("c"))

    reranker = CrossEncoderReranker(model_name="test-model", model=model)
    results = reranker.rerank("query", chunks, top_n=1)

    assert len(results) == 1
    assert results[0].content == "b"


def test_reranker_returns_empty_for_no_chunks() -> None:
    model = MagicMock()

    reranker = CrossEncoderReranker(model_name="test-model", model=model)
    results = reranker.rerank("query", ())

    assert results == ()
    model.predict.assert_not_called()


def test_reranker_passes_query_content_pairs_to_model() -> None:
    model = MagicMock()
    model.predict.return_value = [0.5]

    chunk = _chunk("asyncio.TaskGroup docs")

    reranker = CrossEncoderReranker(model_name="test-model", model=model)
    reranker.rerank("what is TaskGroup", (chunk,))

    model.predict.assert_called_once_with(
        [("what is TaskGroup", "asyncio.TaskGroup docs")]
    )
