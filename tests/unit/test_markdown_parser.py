from hashlib import sha256
from pathlib import Path

from app.documents.parser import MarkdownParser


def test_markdown_parser_preserves_markdown_structure(tmp_path: Path) -> None:
    path = tmp_path / "asyncio.md"
    content = (
        "# Python asyncio\n\n"
        "## Tasks\n\n"
        "Use `asyncio.Task` for asynchronous work.\n\n"
        "```python\n"
        "async def main():\n"
        "    pass\n"
        "```\n"
    )

    path.write_text(content, encoding="utf-8")

    document = MarkdownParser().parse(path)

    assert document.content == content.strip()
    assert document.metadata.title == "Python asyncio"
    assert document.metadata.document_type == "markdown"
    assert document.metadata.source == str(path)
    assert len(document.segments) == 1
    assert document.segments[0].content == content.strip()


def test_markdown_parser_falls_back_to_filename_for_title(
    tmp_path: Path,
) -> None:
    path = tmp_path / "asyncio.md"
    path.write_text(
        "Some documentation without a heading.",
        encoding="utf-8",
    )

    document = MarkdownParser().parse(path)

    assert document.metadata.title == "asyncio"


def test_markdown_parser_normalizes_line_endings(tmp_path: Path) -> None:
    path = tmp_path / "example.md"
    path.write_text(
        "# Title\r\n\r\nSome text\r\n",
        encoding="utf-8",
    )

    document = MarkdownParser().parse(path)

    assert document.content == "# Title\n\nSome text"


def test_markdown_parser_hashes_normalized_content(tmp_path: Path) -> None:
    path = tmp_path / "example.md"
    path.write_text(
        "# Title\r\n",
        encoding="utf-8",
    )

    document = MarkdownParser().parse(path)

    expected_hash = sha256("# Title".encode("utf-8")).hexdigest()

    assert document.content_hash == expected_hash
