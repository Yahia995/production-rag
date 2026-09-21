from uuid import uuid4

from app.retrieval.base import RetrievedChunk
from app.rag.context import ContextChunk
from app.rag.citation import extract_citations


def _context_chunk(index: int, content: str = "example") -> ContextChunk:
    return ContextChunk(
        chunk=RetrievedChunk(
            chunk_id=uuid4(),
            document_id=uuid4(),
            content=content,
            score=1.0,
        ),
        citation_index=index,
    )


def test_extract_citations_finds_referenced_indexes() -> None:
    context_chunks = (_context_chunk(1), _context_chunk(2))

    citations = extract_citations("The answer is here [1].", context_chunks)

    assert len(citations) == 1
    assert citations[0].index == 1


def test_extract_citations_returns_multiple_in_order() -> None:
    context_chunks = (_context_chunk(1), _context_chunk(2), _context_chunk(3))

    citations = extract_citations("See [2] and also [1].", context_chunks)

    assert [c.index for c in citations] == [1, 2]


def test_extract_citations_deduplicates_repeated_markers() -> None:
    context_chunks = (_context_chunk(1),)

    citations = extract_citations("[1] and again [1].", context_chunks)

    assert len(citations) == 1


def test_extract_citations_ignores_unknown_indexes() -> None:
    context_chunks = (_context_chunk(1),)

    citations = extract_citations("See [5].", context_chunks)

    assert citations == ()


def test_extract_citations_returns_empty_for_no_markers() -> None:
    context_chunks = (_context_chunk(1),)

    citations = extract_citations("No citations here.", context_chunks)

    assert citations == ()


def test_citation_preserves_source_information() -> None:
    context_chunk = _context_chunk(1, content="asyncio docs")
    context_chunks = (context_chunk,)

    citations = extract_citations("[1]", context_chunks)

    assert citations[0].document_id == str(context_chunk.chunk.document_id)
    assert citations[0].chunk_id == str(context_chunk.chunk.chunk_id)
    assert citations[0].content == "asyncio docs"
