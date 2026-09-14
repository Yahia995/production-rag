from uuid import uuid4

from app.retrieval.base import RetrievedChunk
from app.retrieval.fusion import reciprocal_rank_fusion


def _chunk(chunk_id, score: float = 1.0) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=uuid4(),
        content="example content",
        score=score,
    )


def test_fusion_ranks_chunk_appearing_in_both_lists_first() -> None:
    shared_id = uuid4()

    dense = (_chunk(shared_id), _chunk(uuid4()))
    sparse = (_chunk(uuid4()), _chunk(shared_id))

    fused = reciprocal_rank_fusion([dense, sparse])

    assert fused[0].chunk_id == shared_id


def test_fusion_combines_disjoint_result_sets() -> None:
    dense_id = uuid4()
    sparse_id = uuid4()

    dense = (_chunk(dense_id),)
    sparse = (_chunk(sparse_id),)

    fused = reciprocal_rank_fusion([dense, sparse])

    fused_ids = {chunk.chunk_id for chunk in fused}
    assert fused_ids == {dense_id, sparse_id}


def test_fusion_handles_empty_result_sets() -> None:
    fused = reciprocal_rank_fusion([(), ()])

    assert fused == ()


def test_fusion_scores_decrease_with_rank() -> None:
    dense = (_chunk(uuid4()), _chunk(uuid4()), _chunk(uuid4()))

    fused = reciprocal_rank_fusion([dense])

    scores = [chunk.score for chunk in fused]
    assert scores == sorted(scores, reverse=True)


def test_fusion_respects_custom_k() -> None:
    chunk_id = uuid4()
    dense = (_chunk(chunk_id),)

    fused_default = reciprocal_rank_fusion([dense])
    fused_custom = reciprocal_rank_fusion([dense], k=10)

    assert fused_default[0].score != fused_custom[0].score


def test_fusion_preserves_chunk_content() -> None:
    chunk_id = uuid4()
    document_id = uuid4()

    dense = (
        RetrievedChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            content="asyncio.TaskGroup docs",
            score=0.9,
            page_number=4,
            section="Tasks",
        ),
    )

    fused = reciprocal_rank_fusion([dense])

    assert fused[0].content == "asyncio.TaskGroup docs"
    assert fused[0].page_number == 4
    assert fused[0].section == "Tasks"
