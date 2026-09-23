from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_rag_pipeline
from app.core.security import verify_api_key
from app.query.transformer import ConversationTurn
from app.rag.pipeline import RagAnswer, RagPipeline

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatTurn] = []
    filters: dict[str, str] | None = None


class CitationResponse(BaseModel):
    index: int
    document_id: str
    chunk_id: str
    content: str
    page_number: int | None = None
    section: str | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]


@router.post(
    "",
    response_model=ChatResponse,
    dependencies=[Depends(verify_api_key)],
)
async def chat(
    request: ChatRequest,
    pipeline: RagPipeline = Depends(get_rag_pipeline),
) -> ChatResponse:
    history = tuple(
        ConversationTurn(role=turn.role, content=turn.content)
        for turn in request.history
    )

    result: RagAnswer = pipeline.answer(
        question=request.question,
        history=history,
        filters=request.filters,
    )

    return ChatResponse(
        answer=result.text,
        citations=[
            CitationResponse(
                index=citation.index,
                document_id=citation.document_id,
                chunk_id=citation.chunk_id,
                content=citation.content,
                page_number=citation.page_number,
                section=citation.section,
            )
            for citation in result.citations
        ],
    )
