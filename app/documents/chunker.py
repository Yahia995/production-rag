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
    """Paragraph-aware chunker with a character-based fallback."""

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

        paragraphs = self._split_paragraphs(content)

        chunks: list[str] = []
        current_parts: list[str] = []
        current_length = 0

        for paragraph in paragraphs:
            if len(paragraph) > self.config.chunk_size:
                if current_parts:
                    chunks.append("\n\n".join(current_parts))
                    current_parts = []
                    current_length = 0

                chunks.extend(self._split_long_paragraph(paragraph))
                continue

            separator_length = 2 if current_parts else 0
            proposed_length = current_length + separator_length + len(paragraph)

            if (
                current_parts
                and proposed_length > self.config.chunk_size
            ):
                chunks.append("\n\n".join(current_parts))

                overlap = self._build_overlap(current_parts)
                current_parts = [overlap, paragraph] if overlap else [paragraph]
                current_length = sum(len(part) for part in current_parts)

                if overlap:
                    current_length += 2
            else:
                current_parts.append(paragraph)
                current_length = proposed_length

        if current_parts:
            chunks.append("\n\n".join(current_parts))

        return tuple(chunks)

    @staticmethod
    def _split_paragraphs(content: str) -> list[str]:
        paragraphs = [
            paragraph.strip()
            for paragraph in content.split("\n\n")
        ]

        return [paragraph for paragraph in paragraphs if paragraph]

    def _split_long_paragraph(self, paragraph: str) -> tuple[str, ...]:
        chunks: list[str] = []
        start = 0

        while start < len(paragraph):
            end = min(
                start + self.config.chunk_size,
                len(paragraph),
            )

            chunk = paragraph[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(paragraph):
                break

            start = end - self.config.chunk_overlap

        return tuple(chunks)

    def _build_overlap(self, parts: list[str]) -> str:
        if self.config.chunk_overlap == 0:
            return ""

        overlap_parts: list[str] = []
        length = 0

        for part in reversed(parts):
            separator_length = 2 if overlap_parts else 0
            proposed_length = length + separator_length + len(part)

            if proposed_length > self.config.chunk_overlap:
                break

            overlap_parts.insert(0, part)
            length = proposed_length

        return "\n\n".join(overlap_parts)
