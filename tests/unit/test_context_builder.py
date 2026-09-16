from uuid import uuid4

from app.retrieval.base import RetrievedChunk
from app.rag.context import ContextBuilder


def _chunk(content: str, chunk_id=None, score: float = 1.0) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id or uuid4(),
        document_id=uuid4(),
        content=content,
        score=score,
    )


def test_context_builder_assigns_sequential_citation_indexes() -> None:
    chunks = (_chunk("first"), _chunk("second"))

    result = ContextBuilder().build(chunks)

    assert [c.citation_index for c in result.chunks] == [1, 2]


def test_context_builder_deduplicates_by_chunk_id() -> None:
    chunk_id = uuid4()
    chunks = (_chunk("first", chunk_id=chunk_id), _chunk("first", chunk_id=chunk_id))

    result = ContextBuilder().build(chunks)

    assert len(result.chunks) == 1


def test_context_builder_formats_prompt_with_citation_markers() -> None:
    chunks = (_chunk("asyncio.TaskGroup manages tasks"),)

    result = ContextBuilder().build(chunks)

    assert result.prompt_context == "[1] asyncio.TaskGroup manages tasks"


def test_context_builder_respects_max_chars_budget() -> None:
    chunks = (_chunk("a" * 50), _chunk("b" * 50), _chunk("c" * 50))

    result = ContextBuilder(max_chars=80).build(chunks)

    assert len(result.chunks) == 1


def test_context_builder_always_includes_at_least_one_chunk() -> None:
    chunks = (_chunk("a" * 500),)

    result = ContextBuilder(max_chars=10).build(chunks)

    assert len(result.chunks) == 1


def test_context_builder_handles_empty_input() -> None:
    result = ContextBuilder().build(())

    assert result.chunks == ()
    assert result.prompt_context == ""
