from pathlib import Path
from uuid import uuid4

import pytest

from app.documents.chunker import (
    CharacterChunker,
    ChunkingConfig,
)
from app.documents.service import DocumentIngestionService


def test_ingestion_service_parses_and_chunks_document(
    tmp_path: Path,
) -> None:
    path = tmp_path / "python.txt"

    path.write_text(
        "Python is a programming language.\n\n"
        "It has a large standard library.",
        encoding="utf-8",
    )

    service = DocumentIngestionService(
        chunker=CharacterChunker(
            ChunkingConfig(
                chunk_size=100,
                chunk_overlap=0,
            ),
        ),
    )

    result = service.ingest(path)

    assert result.document.metadata.title == "python"
    assert result.document.metadata.document_type == "txt"
    assert len(result.chunks) == 1
    assert result.chunks[0].document_id == result.document.document_id
    assert result.chunks[0].content == (
        "Python is a programming language.\n\n"
        "It has a large standard library."
    )


def test_ingestion_service_uses_parser_registry(
    tmp_path: Path,
) -> None:
    path = tmp_path / "guide.md"

    path.write_text(
        "# Python Guide\n\n"
        "Use asyncio for asynchronous programming.",
        encoding="utf-8",
    )

    service = DocumentIngestionService()

    result = service.ingest(path)

    assert result.document.metadata.title == "Python Guide"
    assert result.document.metadata.document_type == "markdown"
    assert result.document.content.startswith("# Python Guide")
    assert len(result.chunks) == 1


def test_ingestion_service_rejects_missing_file(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.txt"

    service = DocumentIngestionService()

    with pytest.raises(
        FileNotFoundError,
        match="Document does not exist",
    ):
        service.ingest(path)


def test_ingestion_service_rejects_directory(
    tmp_path: Path,
) -> None:
    service = DocumentIngestionService()

    with pytest.raises(
        ValueError,
        match="is not a file",
    ):
        service.ingest(tmp_path)


def test_ingestion_service_preserves_document_id_in_chunks(
    tmp_path: Path,
) -> None:
    path = tmp_path / "example.txt"

    path.write_text(
        "First paragraph.\n\n"
        "Second paragraph.",
        encoding="utf-8",
    )

    service = DocumentIngestionService(
        chunker=CharacterChunker(
            ChunkingConfig(
                chunk_size=20,
                chunk_overlap=0,
            ),
        ),
    )

    result = service.ingest(path)

    assert result.document.document_id == result.chunks[0].document_id
    assert all(
        chunk.document_id == result.document.document_id
        for chunk in result.chunks
    )


def test_each_ingestion_creates_a_document_id(
    tmp_path: Path,
) -> None:
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")

    service = DocumentIngestionService()

    first = service.ingest(path)
    second = service.ingest(path)

    assert first.document.document_id != second.document.document_id
    assert first.document.content_hash == second.document.content_hash
