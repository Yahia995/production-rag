from pathlib import Path

from app.documents.models import ParsedDocument
from app.documents.parser import (
    DocumentParser,
    HtmlParser,
    MarkdownParser,
    PdfParser,
    TxtParser,
)


class ParserRegistry:
    """Selects a document parser based on the file extension."""

    def __init__(self) -> None:
        self._parsers: dict[str, DocumentParser] = {
            ".txt": TxtParser(),
            ".md": MarkdownParser(),
            ".markdown": MarkdownParser(),
            ".html": HtmlParser(),
            ".htm": HtmlParser(),
            ".pdf": PdfParser(),
        }

    def get_parser(self, path: Path) -> DocumentParser:
        suffix = path.suffix.lower()

        try:
            return self._parsers[suffix]
        except KeyError as exc:
            supported = ", ".join(sorted(self._parsers))
            raise ValueError(
                f"Unsupported document format: {suffix or '<none>'}. "
                f"Supported formats: {supported}"
            ) from exc

    def parse(self, path: Path) -> ParsedDocument:
        return self.get_parser(path).parse(path)
