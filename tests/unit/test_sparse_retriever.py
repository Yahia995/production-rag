from uuid import uuid4

from app.retrieval.sparse import SparseRetriever


def _indexed_retriever() -> SparseRetriever:
    retriever = SparseRetriever()

    retriever.index(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content="asyncio.TaskGroup manages a group of tasks",
    )
    retriever.index(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content="HTTPException is raised for HTTP errors",
    )
    retriever.index(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content="max_connections controls the connection pool size",
    )

    return retriever


def test_sparse_retriever_finds_exact_term_match() -> None:
    retriever = _indexed_retriever()

    results = retriever.retrieve("asyncio.TaskGroup")

    assert len(results) == 1
    assert "TaskGroup" in results[0].content


def test_sparse_retriever_ranks_by_score_descending() -> None:
    retriever = _indexed_retriever()

    results = retriever.retrieve("connection pool max_connections")

    assert len(results) >= 1
    scores = [result.score for result in results]
    assert scores == sorted(scores, reverse=True)


def test_sparse_retriever_returns_empty_for_no_matches() -> None:
    retriever = _indexed_retriever()

    results = retriever.retrieve("completely unrelated banana")

    assert results == ()


def test_sparse_retriever_respects_top_k() -> None:
    retriever = _indexed_retriever()

    results = retriever.retrieve("HTTPException asyncio max_connections", top_k=1)

    assert len(results) <= 1


def test_sparse_retriever_empty_index_returns_no_results() -> None:
    retriever = SparseRetriever()

    assert retriever.retrieve("anything") == ()


def test_sparse_retriever_filters_by_metadata() -> None:
    retriever = SparseRetriever()

    match_id = uuid4()
    other_id = uuid4()

    retriever.index(
        chunk_id=match_id,
        document_id=uuid4(),
        content="connection pooling configuration",
        metadata={"collection": "python"},
    )
    retriever.index(
        chunk_id=other_id,
        document_id=uuid4(),
        content="connection pooling configuration",
        metadata={"collection": "other"},
    )

    results = retriever.retrieve(
        "connection pooling",
        filters={"collection": "python"},
    )

    assert len(results) == 1
    assert results[0].chunk_id == match_id
