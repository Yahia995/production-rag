from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    source: str
    title: str
    document_type: str
    collection: str
    version: str | None = None
    tags: tuple[str, ...] = ()
    extra: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    document_id: UUID
    content: str
    metadata: DocumentMetadata
    content_hash: str
    parsed_at: datetime
