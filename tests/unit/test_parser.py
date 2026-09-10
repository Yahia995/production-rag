from pathlib import Path

import pytest

from app.documents.parser import DocumentParser


def test_document_parser_is_abstract() -> None:
    with pytest.raises(TypeError):
        DocumentParser()  # type: ignore[abstract]


def test_document_parser_requires_parse_implementation() -> None:
    class IncompleteParser(DocumentParser):
        pass

    with pytest.raises(TypeError):
        IncompleteParser()  # type: ignore[abstract]


def test_document_parser_implementation_can_be_used() -> None:
    class TestParser(DocumentParser):
        def parse(self, path: Path):
            raise NotImplementedError

    parser = TestParser()

    assert isinstance(parser, DocumentParser)
