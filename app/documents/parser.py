from abc import ABC, abstractmethod
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from bs4 import BeautifulSoup
from pypdf import PdfReader

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


class MarkdownParser(DocumentParser):
    """Parser for Markdown documents."""

    def parse(self, path: Path) -> ParsedDocument:
        content = path.read_text(encoding="utf-8")
        content = self._normalize(content)

        metadata = DocumentMetadata(
            source=str(path),
            title=self._extract_title(content, path),
            document_type="markdown",
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

    @staticmethod
    def _extract_title(content: str, path: Path) -> str:
        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith("# "):
                return stripped[2:].strip()

        return path.stem


class HtmlParser(DocumentParser):
    """Parser for HTML documents."""

    def parse(self, path: Path) -> ParsedDocument:
        html = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        title = self._extract_title(soup, path)

        for element in soup(["title", "script", "style", "noscript"]):
            element.decompose()

        content = self._normalize(soup.get_text("\n"))

        metadata = DocumentMetadata(
            source=str(path),
            title=title,
            document_type="html",
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
    def _extract_title(soup: BeautifulSoup, path: Path) -> str:
        if soup.title is not None:
            title = soup.title.get_text(" ", strip=True)

            if title:
                return title

        heading = soup.find("h1")

        if heading is not None:
            title = heading.get_text(" ", strip=True)

            if title:
                return title

        return path.stem

    @staticmethod
    def _normalize(content: str) -> str:
        lines = [line.strip() for line in content.splitlines()]
        lines = [line for line in lines if line]

        return "\n".join(lines)


class PdfParser(DocumentParser):
    """Parser for text-based PDF documents."""

    def parse(self, path: Path) -> ParsedDocument:
        reader = PdfReader(str(path))

        pages: list[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""
            text = self._normalize_page(text)

            if text:
                pages.append(text)

        content = "\n\n".join(pages)

        metadata = DocumentMetadata(
            source=str(path),
            title=self._extract_title(reader, path),
            document_type="pdf",
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
    def _normalize_page(content: str) -> str:
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        lines = [line.strip() for line in content.splitlines()]
        lines = [line for line in lines if line]

        return "\n".join(lines)

    @staticmethod
    def _extract_title(reader: PdfReader, path: Path) -> str:
        metadata = reader.metadata

        if metadata is not None and metadata.title:
            title = str(metadata.title).strip()

            if title:
                return title

        return path.stem
