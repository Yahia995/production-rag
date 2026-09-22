from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_ingestion_queue
from app.core.queue import IngestionJobMessage, RedisJobQueue

router = APIRouter(prefix="/documents", tags=["documents"])


class CreateDocumentRequest(BaseModel):
    source: str
    collection: str = "default"


class IngestionJobResponse(BaseModel):
    job_id: str
    source: str
    collection: str
    status: str


@router.post("", response_model=IngestionJobResponse, status_code=202)
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


@router.post("/batch", response_model=list[IngestionJobResponse], status_code=202)
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
