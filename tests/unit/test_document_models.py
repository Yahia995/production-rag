from datetime import datetime, timezone
from uuid import uuid4

from app.documents.models import DocumentMetadata, ParsedDocument, ParsedSegment


def test_document_metadata_defaults() -> None:
    metadata = DocumentMetadata(
        source="https://docs.python.org/",
        title="Python Documentation",
        document_type="html",
        collection="python",
    )

    assert metadata.version is None
    assert metadata.tags == ()
    assert metadata.extra == {}


def test_parsed_segment_defaults() -> None:
    segment = ParsedSegment(
        content="Python is a programming language.",
    )

    assert segment.content == "Python is a programming language."
    assert segment.page_number is None
    assert segment.section is None


def test_parsed_document_contains_normalized_content_and_metadata() -> None:
    document_id = uuid4()
    parsed_at = datetime.now(timezone.utc)

    metadata = DocumentMetadata(
        source="docs/python.md",
        title="Python Guide",
        document_type="markdown",
        collection="python",
        version="3.13",
        tags=("official", "guide"),
    )

    segment = ParsedSegment(
        content="Python is a programming language.",
        section="Introduction",
    )

    document = ParsedDocument(
        document_id=document_id,
        content="Python is a programming language.",
        metadata=metadata,
        content_hash="abc123",
        parsed_at=parsed_at,
        segments=(segment,),
    )

    assert document.document_id == document_id
    assert document.content == "Python is a programming language."
    assert document.metadata.title == "Python Guide"
    assert document.metadata.version == "3.13"
    assert document.content_hash == "abc123"
    assert document.parsed_at == parsed_at
    assert document.segments == (segment,)
    assert document.segments[0].section == "Introduction"
