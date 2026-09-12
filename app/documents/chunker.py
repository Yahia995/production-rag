from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID, uuid4

from app.documents.models import ParsedDocument, ParsedSegment


@dataclass(frozen=True, slots=True)
class ChunkingConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 150

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    chunk_id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    page_number: int | None = None
    section: str | None = None


class DocumentChunker(ABC):
    """Interface implemented by document chunkers."""

    @abstractmethod
    def chunk(self, document: ParsedDocument) -> tuple[DocumentChunk, ...]:
        """Split a parsed document into chunks."""
        raise NotImplementedError


class CharacterChunker(DocumentChunker):
    """Deterministic character-based chunker with overlap."""

    def __init__(self, config: ChunkingConfig | None = None) -> None:
        self.config = config or ChunkingConfig()

    def chunk(self, document: ParsedDocument) -> tuple[DocumentChunk, ...]:
        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for segment in document.segments:
            segment_chunks = self._chunk_segment(segment)

            for content in segment_chunks:
                chunks.append(
                    DocumentChunk(
                        chunk_id=uuid4(),
                        document_id=document.document_id,
                        content=content,
                        chunk_index=chunk_index,
                        page_number=segment.page_number,
                        section=segment.section,
                    )
                )
                chunk_index += 1

        return tuple(chunks)

    def _chunk_segment(self, segment: ParsedSegment) -> tuple[str, ...]:
        content = segment.content.strip()

        if not content:
            return ()

        if len(content) <= self.config.chunk_size:
            return (content,)

        chunks: list[str] = []
        start = 0

        while start < len(content):
            end = min(
                start + self.config.chunk_size,
                len(content),
            )

            chunk = content[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(content):
                break

            start = end - self.config.chunk_overlap

        return tuple(chunks)
