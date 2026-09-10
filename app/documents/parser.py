from abc import ABC, abstractmethod
from hashlib import sha256
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

from app.documents.models import DocumentMetadata, ParsedDocument


class DocumentParser(ABC):
    """Interface implemented by document-format parsers."""

    @abstractmethod
    def parse(self, path: Path) -> ParsedDocument:
        """Parse a document and return its normalized representation."""
        raise NotImplementedError


class TxtParser(DocumentParser):
    """Parser for UTF-8 plain-text documents."""

    def parse(self, path: Path) -> ParsedDocument:
        content = path.read_text(encoding="utf-8")
        content = self._normalize(content)

        metadata = DocumentMetadata(
            source=str(path),
            title=path.stem,
            document_type="txt",
            collection="default",
        )

        content_hash = sha256(content.encode("utf-8")).hexdigest()

        return ParsedDocument(
            document_id=uuid4(),
            content=content,
            metadata=metadata,
            content_hash=content_hash,
            parsed_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _normalize(content: str) -> str:
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        return content.strip()
