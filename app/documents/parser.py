from abc import ABC, abstractmethod
from pathlib import Path

from app.documents.models import ParsedDocument


class DocumentParser(ABC):
    """Interface implemented by document-format parsers."""

    @abstractmethod
    def parse(self, path: Path) -> ParsedDocument:
        """Parse a document and return its normalized representation."""
        raise NotImplementedError
