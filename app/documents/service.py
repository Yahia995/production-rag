from dataclasses import dataclass
from pathlib import Path

from app.documents.chunker import DocumentChunk, DocumentChunker
from app.documents.models import ParsedDocument
from app.documents.registry import ParserRegistry


@dataclass(frozen=True, slots=True)
class IngestionResult:
    document: ParsedDocument
    chunks: tuple[DocumentChunk, ...]


class DocumentIngestionService:
    """Coordinates document parsing and chunking."""

    def __init__(
        self,
        parser_registry: ParserRegistry | None = None,
        chunker: DocumentChunker | None = None,
    ) -> None:
        self.parser_registry = parser_registry or ParserRegistry()

        if chunker is None:
            from app.documents.chunker import CharacterChunker

            chunker = CharacterChunker()

        self.chunker = chunker

    def ingest(self, path: Path) -> IngestionResult:
        if not path.exists():
            raise FileNotFoundError(f"Document does not exist: {path}")

        if not path.is_file():
            raise ValueError(f"Document path is not a file: {path}")

        document = self.parser_registry.parse(path)
        chunks = self.chunker.chunk(document)

        return IngestionResult(
            document=document,
            chunks=chunks,
        )
