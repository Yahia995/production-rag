from app.retrieval.base import RetrievedChunk


def reciprocal_rank_fusion(
    result_sets: list[tuple[RetrievedChunk, ...]],
    k: int = 60,
) -> tuple[RetrievedChunk, ...]:
    """Combine multiple ranked result sets using Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    chunks_by_id: dict[str, RetrievedChunk] = {}

    for results in result_sets:
        for rank, chunk in enumerate(results, start=1):
            key = str(chunk.chunk_id)

            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)

            if key not in chunks_by_id or chunk.score > chunks_by_id[key].score:
                chunks_by_id[key] = chunk

    ranked_keys = sorted(scores, key=lambda key: scores[key], reverse=True)

    return tuple(
        RetrievedChunk(
            chunk_id=chunks_by_id[key].chunk_id,
            document_id=chunks_by_id[key].document_id,
            content=chunks_by_id[key].content,
            score=scores[key],
            page_number=chunks_by_id[key].page_number,
            section=chunks_by_id[key].section,
        )
        for key in ranked_keys
    )
