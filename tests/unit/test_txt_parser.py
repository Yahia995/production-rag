from hashlib import sha256
from pathlib import Path

from app.documents.parser import TxtParser


def test_txt_parser_reads_and_normalizes_content(tmp_path: Path) -> None:
    path = tmp_path / "python-guide.txt"
    path.write_text(
        "  First line\r\nSecond line\r\n\r\n",
        encoding="utf-8",
    )

    document = TxtParser().parse(path)

    assert document.content == "First line\nSecond line"
    assert document.metadata.source == str(path)
    assert document.metadata.title == "python-guide"
    assert document.metadata.document_type == "txt"
    assert document.metadata.collection == "default"
    assert len(document.segments) == 1
    assert document.segments[0].content == document.content
    assert document.segments[0].page_number is None


def test_txt_parser_generates_content_hash(tmp_path: Path) -> None:
    path = tmp_path / "example.txt"
    path.write_text("hello world\n", encoding="utf-8")

    document = TxtParser().parse(path)

    expected_hash = sha256("hello world".encode("utf-8")).hexdigest()

    assert document.content_hash == expected_hash


def test_txt_parser_generates_document_id(tmp_path: Path) -> None:
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")

    document = TxtParser().parse(path)

    assert document.document_id is not None
