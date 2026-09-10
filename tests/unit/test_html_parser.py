from hashlib import sha256
from pathlib import Path

from app.documents.parser import HtmlParser


def test_html_parser_extracts_readable_content(tmp_path: Path) -> None:
    path = tmp_path / "python.html"

    path.write_text(
        """<!doctype html>
<html>
<head>
    <title>Python Documentation</title>
    <style>body { color: red; }</style>
</head>
<body>
    <nav>Navigation</nav>
    <main>
        <h1>Python</h1>
        <p>Python is a programming language.</p>
        <script>alert("ignore");</script>
        <p>It has a large standard library.</p>
    </main>
</body>
</html>
""",
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


def test_html_parser_falls_back_to_h1_for_title(tmp_path: Path) -> None:
    path = tmp_path / "python.html"

    path.write_text(
        """
        <html>
            <body>
                <h1>Python Guide</h1>
                <p>Introduction.</p>
            </body>
        </html>
        """,
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
