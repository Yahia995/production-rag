from uuid import uuid4

from app.documents.chunker import DocumentChunk


def test_document_chunk_contains_required_fields() -> None:
    document_id = uuid4()
    chunk_id = uuid4()

    chunk = DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content="Python is a programming language.",
        chunk_index=0,
    )

    assert chunk.chunk_id == chunk_id
    assert chunk.document_id == document_id
    assert chunk.content == "Python is a programming language."
    assert chunk.chunk_index == 0
    assert chunk.page_number is None
    assert chunk.section is None


def test_document_chunk_preserves_source_location() -> None:
    document_id = uuid4()

    chunk = DocumentChunk(
        chunk_id=uuid4(),
        document_id=document_id,
        content="Asyncio provides asynchronous programming.",
        chunk_index=3,
        page_number=12,
        section="Tasks",
    )

    assert chunk.document_id == document_id
    assert chunk.chunk_index == 3
    assert chunk.page_number == 12
    assert chunk.section == "Tasks"
