from uuid import UUID, uuid4

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_ingestion_queue, get_db, get_vector_store
from app.core.queue import IngestionJobMessage, RedisJobQueue
from app.db.qdrant import QdrantVectorStore
from app.documents.repository import DocumentRepository

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/documents", tags=["documents"])


class CreateDocumentRequest(BaseModel):
    source: str
    collection: str = "default"


class IngestionJobResponse(BaseModel):
    job_id: str
    source: str
    collection: str
    status: str


@router.post("", response_model=IngestionJobResponse, status_code=202, dependencies=[Depends(verify_api_key)])
async def create_document(
    request: CreateDocumentRequest,
    queue: RedisJobQueue = Depends(get_ingestion_queue),
) -> IngestionJobResponse:
    job_id = str(uuid4())

    message = IngestionJobMessage(
        job_id=job_id,
        source=request.source,
        collection=request.collection,
    )

    queue.enqueue(message)

    return IngestionJobResponse(
        job_id=job_id,
        source=request.source,
        collection=request.collection,
        status="pending",
    )


@router.post("/batch", response_model=list[IngestionJobResponse], status_code=202, dependencies=[Depends(verify_api_key)])
async def create_documents_batch(
    requests: list[CreateDocumentRequest],
    queue: RedisJobQueue = Depends(get_ingestion_queue),
) -> list[IngestionJobResponse]:
    if not requests:
        raise HTTPException(status_code=400, detail="Batch cannot be empty")

    responses = []

    for request in requests:
        job_id = str(uuid4())

        queue.enqueue(
            IngestionJobMessage(
                job_id=job_id,
                source=request.source,
                collection=request.collection,
            )
        )

        responses.append(
            IngestionJobResponse(
                job_id=job_id,
                source=request.source,
                collection=request.collection,
                status="pending",
            )
        )

    return responses


class DocumentResponse(BaseModel):
    id: UUID
    source: str
    title: str
    document_type: str
    collection: str
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=list[DocumentResponse], dependencies=[Depends(verify_api_key)])
async def list_documents(
    collection: str | None = None,
    session: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    repository = DocumentRepository(session)
    documents = await repository.list_documents(collection=collection)

    return [DocumentResponse.model_validate(document, from_attributes=True) for document in documents]


@router.get("/{document_id}", response_model=DocumentResponse, dependencies=[Depends(verify_api_key)])
async def get_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    repository = DocumentRepository(session)
    document = await repository.get_document(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse.model_validate(document, from_attributes=True)


@router.delete("/{document_id}", status_code=204, dependencies=[Depends(verify_api_key)])
async def delete_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_db),
    vector_store: QdrantVectorStore = Depends(get_vector_store),
) -> None:
    repository = DocumentRepository(session)
    deleted = await repository.delete_document(document_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    vector_store.delete_document(document_id)
