from unittest.mock import MagicMock
from uuid import uuid4

from app.core.metrics import rag_requests_total
from app.generation.base import GenerationResult
from app.rag.pipeline import RagPipeline
from app.retrieval.base import RetrievedChunk


def _chunk(content: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content=content,
        score=0.9,
    )


def _pipeline(dense_results=(), sparse_results=(), reranked=(), answer_text="answer"):
    dense_retriever = MagicMock()
    dense_retriever.retrieve.return_value = dense_results

    sparse_retriever = MagicMock()
    sparse_retriever.retrieve.return_value = sparse_results

    reranker = MagicMock()
    reranker.rerank.return_value = reranked

    llm_provider = MagicMock()
    llm_provider.generate.return_value = GenerationResult(
        text=answer_text, model="test-model"
    )

    pipeline = RagPipeline(
        dense_retriever=dense_retriever,
        sparse_retriever=sparse_retriever,
        reranker=reranker,
        llm_provider=llm_provider,
    )

    return pipeline, dense_retriever, sparse_retriever, reranker, llm_provider


def test_pipeline_calls_both_retrievers_with_query() -> None:
    pipeline, dense_retriever, sparse_retriever, _, _ = _pipeline()

    pipeline.answer("What is connection pooling?")

    dense_retriever.retrieve.assert_called_once()
    sparse_retriever.retrieve.assert_called_once()


def test_pipeline_reranks_fused_results() -> None:
    chunk = _chunk("connection pooling reuses connections")

    pipeline, _, _, reranker, _ = _pipeline(
        dense_results=(chunk,),
        reranked=(chunk,),
    )

    pipeline.answer("What is connection pooling?")

    reranker.rerank.assert_called_once()


def test_pipeline_returns_answer_with_citations() -> None:
    chunk = _chunk("connection pooling reuses connections")

    pipeline, _, _, _, _ = _pipeline(
        dense_results=(chunk,),
        reranked=(chunk,),
        answer_text="Pooling reuses connections [1].",
    )

    result = pipeline.answer("What is connection pooling?")

    assert result.text == "Pooling reuses connections [1]."
    assert len(result.citations) == 1
    assert result.citations[0].content == chunk.content


def test_pipeline_uses_query_transformer_when_provided() -> None:
    query_transformer = MagicMock()
    query_transformer.transform.return_value = "rewritten query"

    pipeline, dense_retriever, _, _, _ = _pipeline()
    pipeline.query_transformer = query_transformer

    pipeline.answer("How is it configured?")

    query_transformer.transform.assert_called_once()
    args, _ = dense_retriever.retrieve.call_args
    assert args[0] == "rewritten query"


def test_pipeline_skips_query_transformation_when_not_configured() -> None:
    pipeline, dense_retriever, _, _, _ = _pipeline()

    pipeline.answer("What is asyncio?")

    args, _ = dense_retriever.retrieve.call_args
    assert args[0] == "What is asyncio?"


def test_pipeline_returns_no_citations_when_answer_has_none() -> None:
    chunk = _chunk("some content")

    pipeline, _, _, _, _ = _pipeline(
        dense_results=(chunk,),
        reranked=(chunk,),
        answer_text="I don't have enough information to answer that.",
    )

    result = pipeline.answer("unrelated question")

    assert result.citations == ()


def test_pipeline_increments_request_counter() -> None:
    pipeline, _, _, _, _ = _pipeline()

    before = rag_requests_total._value.get()
    pipeline.answer("What is connection pooling?")
    after = rag_requests_total._value.get()

    assert after == before + 1
