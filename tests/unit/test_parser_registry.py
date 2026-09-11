from pathlib import Path

import pytest

from app.documents.parser import (
    HtmlParser,
    MarkdownParser,
    PdfParser,
    TxtParser,
)
from app.documents.registry import ParserRegistry


@pytest.fixture
def registry() -> ParserRegistry:
    return ParserRegistry()


@pytest.mark.parametrize(
    ("filename", "parser_type"),
    [
        ("document.txt", TxtParser),
        ("document.md", MarkdownParser),
        ("document.markdown", MarkdownParser),
        ("document.html", HtmlParser),
        ("document.htm", HtmlParser),
        ("document.pdf", PdfParser),
    ],
)
def test_registry_selects_parser(
    registry: ParserRegistry,
    filename: str,
    parser_type: type,
) -> None:
    parser = registry.get_parser(Path(filename))

    assert isinstance(parser, parser_type)


def test_registry_is_case_insensitive(registry: ParserRegistry) -> None:
    assert isinstance(
        registry.get_parser(Path("DOCUMENT.PDF")),
        PdfParser,
    )

    assert isinstance(
        registry.get_parser(Path("DOCUMENT.MD")),
        MarkdownParser,
    )


@pytest.mark.parametrize(
    "filename",
    [
        "document.docx",
        "document.csv",
        "document",
        ".unknown",
    ],
)
def test_registry_rejects_unsupported_format(
    registry: ParserRegistry,
    filename: str,
) -> None:
    with pytest.raises(ValueError, match="Unsupported document format"):
        registry.get_parser(Path(filename))
