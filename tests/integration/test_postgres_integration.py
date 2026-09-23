from uuid import uuid4

import pytest
from sqlalchemy import select

from app.db.models.documents import Document, DocumentVersion

pytestmark = pytest.mark.asyncio


async def test_document_can_be_inserted_and_read_back(db_session) -> None:
    document = Document(
        source="docs/asyncio.md",
        title="Asyncio",
        document_type="markdown",
        collection="python",
    )

    db_session.add(document)
    await db_session.commit()

    result = await db_session.execute(select(Document).where(Document.id == document.id))
    fetched = result.scalar_one()

    assert fetched.title == "Asyncio"


async def test_document_version_cascade_delete(db_session) -> None:
    document = Document(
        source="docs/asyncio.md",
        title="Asyncio",
        document_type="markdown",
        collection="python",
    )
    version = DocumentVersion(
        document=document,
        version="1",
        content_hash="abc123",
        content="asyncio content",
    )

    db_session.add(document)
    db_session.add(version)
    await db_session.commit()

    await db_session.delete(document)
    await db_session.commit()

    result = await db_session.execute(
        select(DocumentVersion).where(DocumentVersion.id == version.id)
    )

    assert result.scalar_one_or_none() is None


async def test_document_requires_source(db_session) -> None:
    from sqlalchemy.exc import IntegrityError

    document = Document(
        source=None,
        title="Asyncio",
        document_type="markdown",
        collection="python",
    )

    db_session.add(document)

    with pytest.raises(IntegrityError):
        await db_session.commit()
