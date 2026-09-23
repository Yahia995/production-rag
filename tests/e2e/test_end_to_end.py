from pathlib import Path
from unittest.mock import MagicMock

from app.documents.service import DocumentIngestionService
from app.db.qdrant import VectorRecord
from app.generation.base import GenerationResult
from app.rag.pipeline import RagPipeline
from app.reranking.base import Reranker


class _PassthroughReranker(Reranker):
    def rerank(self, query, chunks, top_n=5):
        return chunks[:top_n]


def test_upload_ingest_index_ask_and_verify_citation(
    tmp_path: Path,
    embedding_provider,
    vector_store,
    dense_retriever,
    sparse_retriever,
) -> None:
    document_path = tmp_path / "asyncio.md"
    document_path.write_text(
        "# Asyncio\n\n"
        "asyncio.TaskGroup manages a group of related asyncio tasks "
        "and cancels them together on failure.",
        encoding="utf-8",
    )

    ingestion_service = DocumentIngestionService()
    result = ingestion_service.ingest(document_path)

    for chunk in result.chunks:
        vector = embedding_provider.embed_query(chunk.content)
        vector_store.upsert(
            [
                VectorRecord(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    vector=vector,
                    content=chunk.content,
                )
            ]
        )
        sparse_retriever.index(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            content=chunk.content,
        )

    llm_provider = MagicMock()
    llm_provider.generate.return_value = GenerationResult(
        text="TaskGroup manages related asyncio tasks and cancels them together [1].",
        model="test-model",
    )

    pipeline = RagPipeline(
        dense_retriever=dense_retriever,
        sparse_retriever=sparse_retriever,
        reranker=_PassthroughReranker(),
        llm_provider=llm_provider,
    )

    answer = pipeline.answer("What does asyncio.TaskGroup do?")

    assert "TaskGroup" in answer.text
    assert len(answer.citations) == 1
    assert answer.citations[0].document_id == str(result.document.document_id)
