from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    chunk_id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    page_number: int | None = None
    section: str | None = None
