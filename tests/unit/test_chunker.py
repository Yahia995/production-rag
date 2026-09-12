from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.documents.chunker import (
    CharacterChunker,
    ChunkingConfig,
    DocumentChunk,
    DocumentChunker,
)
from app.documents.models import DocumentMetadata, ParsedDocument, ParsedSegment


def _document(
    content: str,
    *,
    page_number: int | None = None,
    section: str | None = None,
) -> ParsedDocument:
    document_id = uuid4()

    return ParsedDocument(
        document_id=document_id,
        content=content,
        metadata=DocumentMetadata(
            source="example.txt",
            title="Example",
            document_type="txt",
            collection="default",
        ),
        content_hash="abc123",
        parsed_at=datetime.now(timezone.utc),
        segments=(
            ParsedSegment(
                content=content,
                page_number=page_number,
                section=section,
            ),
        ),
    )


def test_chunking_config_defaults() -> None:
    config = ChunkingConfig()

    assert config.chunk_size == 1000
    assert config.chunk_overlap == 150


def test_chunking_config_rejects_zero_size() -> None:
    with pytest.raises(ValueError, match="chunk_size"):
        ChunkingConfig(chunk_size=0)


def test_chunking_config_rejects_negative_overlap() -> None:
    with pytest.raises(ValueError, match="chunk_overlap"):
        ChunkingConfig(
            chunk_size=100,
            chunk_overlap=-1,
        )


def test_chunking_config_rejects_overlap_equal_to_size() -> None:
    with pytest.raises(ValueError, match="smaller than chunk_size"):
        ChunkingConfig(
            chunk_size=100,
            chunk_overlap=100,
        )


def test_small_document_produces_one_chunk() -> None:
    document = _document("Python is a programming language.")

    chunks = CharacterChunker(
        ChunkingConfig(chunk_size=100, chunk_overlap=20),
    ).chunk(document)

    assert len(chunks) == 1
    assert chunks[0].content == "Python is a programming language."
    assert chunks[0].chunk_index == 0
    assert chunks[0].document_id == document.document_id


def test_large_document_is_split_into_overlapping_chunks() -> None:
    document = _document("abcdefghij")

    chunks = CharacterChunker(
        ChunkingConfig(
            chunk_size=5,
            chunk_overlap=2,
        ),
    ).chunk(document)

    assert [chunk.content for chunk in chunks] == [
        "abcde",
        "defgh",
        "ghij",
    ]


def test_chunk_indexes_are_sequential() -> None:
    document = _document("abcdefghij")

    chunks = CharacterChunker(
        ChunkingConfig(
            chunk_size=4,
            chunk_overlap=1,
        ),
    ).chunk(document)

    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]


def test_source_metadata_is_preserved() -> None:
    document = _document(
        "Python asyncio provides asynchronous programming.",
        page_number=12,
        section="Tasks",
    )

    chunks = CharacterChunker(
        ChunkingConfig(chunk_size=100, chunk_overlap=20),
    ).chunk(document)

    assert len(chunks) == 1
    assert chunks[0].page_number == 12
    assert chunks[0].section == "Tasks"


def test_empty_segment_produces_no_chunks() -> None:
    document = _document("")

    chunks = CharacterChunker().chunk(document)

    assert chunks == ()


def test_multiple_segments_preserve_document_order() -> None:
    document_id = uuid4()

    document = ParsedDocument(
        document_id=document_id,
        content="First page\n\nSecond page",
        metadata=DocumentMetadata(
            source="example.pdf",
            title="Example",
            document_type="pdf",
            collection="default",
        ),
        content_hash="abc123",
        parsed_at=datetime.now(timezone.utc),
        segments=(
            ParsedSegment(
                content="First page",
                page_number=1,
            ),
            ParsedSegment(
                content="Second page",
                page_number=2,
            ),
        ),
    )

    chunks = CharacterChunker(
        ChunkingConfig(chunk_size=100, chunk_overlap=20),
    ).chunk(document)

    assert [chunk.content for chunk in chunks] == [
        "First page",
        "Second page",
    ]
    assert [chunk.page_number for chunk in chunks] == [1, 2]
    assert [chunk.chunk_index for chunk in chunks] == [0, 1]


def test_document_chunker_is_abstract() -> None:
    with pytest.raises(TypeError):
        DocumentChunker()  # type: ignore[abstract]


def test_document_chunk_is_immutable() -> None:
    chunk = DocumentChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content="hello",
        chunk_index=0,
    )

    with pytest.raises(AttributeError):
        chunk.content = "changed"  # type: ignore[misc]
