from sentence_transformers import CrossEncoder

from app.retrieval.base import RetrievedChunk
from app.reranking.base import Reranker


class CrossEncoderReranker(Reranker):
    """Reranker backed by a cross-encoder relevance model."""

    def __init__(self, model_name: str, model: CrossEncoder | None = None) -> None:
        self.model_name = model_name
        self.model = model or CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        chunks: tuple[RetrievedChunk, ...],
        top_n: int = 5,
    ) -> tuple[RetrievedChunk, ...]:
        if not chunks:
            return ()

        pairs = [(query, chunk.content) for chunk in chunks]
        scores = self.model.predict(pairs)

        scored_chunks = [
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                score=float(score),
                page_number=chunk.page_number,
                section=chunk.section,
            )
            for chunk, score in zip(chunks, scores, strict=True)
        ]

        scored_chunks.sort(key=lambda chunk: chunk.score, reverse=True)

        return tuple(scored_chunks[:top_n])
