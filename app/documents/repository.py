from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.documents import Document


class DocumentRepository:
    """Data access for documents backed by PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_documents(self, collection: str | None = None) -> list[Document]:
        statement = select(Document)

        if collection is not None:
            statement = statement.where(Document.collection == collection)

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_document(self, document_id: UUID) -> Document | None:
        return await self.session.get(Document, document_id)

    async def delete_document(self, document_id: UUID) -> bool:
        document = await self.session.get(Document, document_id)

        if document is None:
            return False

        await self.session.delete(document)
        await self.session.commit()

        return True
