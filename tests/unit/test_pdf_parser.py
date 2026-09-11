from hashlib import sha256
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.documents.parser import PdfParser


def _create_pdf(path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)

    with path.open("wb") as file:
        writer.write(file)


def test_pdf_parser_reads_pdf_metadata(tmp_path: Path) -> None:
    path = tmp_path / "python-guide.pdf"

    _create_pdf(path)

    document = PdfParser().parse(path)

    assert document.metadata.source == str(path)
    assert document.metadata.title == "python-guide"
    assert document.metadata.document_type == "pdf"
    assert document.metadata.collection == "default"


def test_pdf_parser_returns_empty_content_for_blank_pdf(
    tmp_path: Path,
) -> None:
    path = tmp_path / "empty.pdf"

    _create_pdf(path)

    document = PdfParser().parse(path)

    assert document.content == ""
    assert document.content_hash == sha256(b"").hexdigest()


def test_created_pdf_can_be_read_by_pypdf(tmp_path: Path) -> None:
    path = tmp_path / "example.pdf"

    _create_pdf(path)

    reader = PdfReader(str(path))

    assert len(reader.pages) == 1
