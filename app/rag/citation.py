import re
from dataclasses import dataclass

from app.rag.context import ContextChunk

_CITATION_PATTERN = re.compile(r"\[(\d+)\]")


@dataclass(frozen=True, slots=True)
class Citation:
    index: int
    document_id: str
    chunk_id: str
    content: str
    page_number: int | None = None
    section: str | None = None


def extract_citations(
    answer_text: str,
    context_chunks: tuple[ContextChunk, ...],
) -> tuple[Citation, ...]:
    """Extract citations that were actually referenced in the answer text."""
    chunks_by_index = {
        context_chunk.citation_index: context_chunk
        for context_chunk in context_chunks
    }

    cited_indexes = sorted(
        {int(match) for match in _CITATION_PATTERN.findall(answer_text)}
    )

    citations = []

    for index in cited_indexes:
        context_chunk = chunks_by_index.get(index)

        if context_chunk is None:
            continue

        citations.append(
            Citation(
                index=index,
                document_id=str(context_chunk.chunk.document_id),
                chunk_id=str(context_chunk.chunk.chunk_id),
                content=context_chunk.chunk.content,
                page_number=context_chunk.chunk.page_number,
                section=context_chunk.chunk.section,
            )
        )

    return tuple(citations)
