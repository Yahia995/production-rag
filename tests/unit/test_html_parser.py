from hashlib import sha256
from pathlib import Path

from app.documents.parser import HtmlParser


def test_html_parser_extracts_readable_content(tmp_path: Path) -> None:
    path = tmp_path / "python.html"

    path.write_text(
        "<!doctype html>\n"
        "<html>\n"
        "<head>\n"
        "    <title>Python Documentation</title>\n"
        "    <style>body { color: red; }</style>\n"
        "</head>\n"
        "<body>\n"
        "    <nav>Navigation</nav>\n"
        "    <main>\n"
        "        <h1>Python</h1>\n"
        "        <p>Python is a programming language.</p>\n"
        "        <script>alert(\"ignore\");</script>\n"
        "        <p>It has a large standard library.</p>\n"
        "    </main>\n"
        "</body>\n"
        "</html>\n",
        encoding="utf-8",
    )

    document = HtmlParser().parse(path)

    assert document.metadata.title == "Python Documentation"
    assert document.metadata.document_type == "html"
    assert document.content == (
        "Navigation\n"
        "Python\n"
        "Python is a programming language.\n"
        "It has a large standard library."
    )
    assert len(document.segments) == 1
    assert document.segments[0].content == document.content


def test_html_parser_falls_back_to_h1_for_title(tmp_path: Path) -> None:
    path = tmp_path / "python.html"

    path.write_text(
        "<html>\n"
        "    <body>\n"
        "        <h1>Python Guide</h1>\n"
        "        <p>Introduction.</p>\n"
        "    </body>\n"
        "</html>\n",
        encoding="utf-8",
    )

    document = HtmlParser().parse(path)

    assert document.metadata.title == "Python Guide"


def test_html_parser_falls_back_to_filename_for_title(tmp_path: Path) -> None:
    path = tmp_path / "python-guide.html"

    path.write_text(
        "<html><body><p>No title here.</p></body></html>",
        encoding="utf-8",
    )

    document = HtmlParser().parse(path)

    assert document.metadata.title == "python-guide"


def test_html_parser_hashes_normalized_content(tmp_path: Path) -> None:
    path = tmp_path / "example.html"

    path.write_text(
        "<html><body><p>Hello</p></body></html>",
        encoding="utf-8",
    )

    document = HtmlParser().parse(path)

    expected_hash = sha256("Hello".encode("utf-8")).hexdigest()

    assert document.content_hash == expected_hash
