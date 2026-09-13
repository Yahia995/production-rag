from unittest.mock import MagicMock
from uuid import uuid4

from app.retrieval.dense import DenseRetriever


def test_dense_retriever_embeds_query_before_search() -> None:
    embedding_provider = MagicMock()
    embedding_provider.embed_query.return_value = [0.1, 0.2]

    vector_store = MagicMock()
    vector_store.search.return_value = []

    retriever = DenseRetriever(embedding_provider, vector_store)
    retriever.retrieve("connection pooling")

    embedding_provider.embed_query.assert_called_once_with("connection pooling")
    vector_store.search.assert_called_once()


def test_dense_retriever_maps_results_to_retrieved_chunks() -> None:
    document_id = uuid4()
    chunk_id = uuid4()

    embedding_provider = MagicMock()
    embedding_provider.embed_query.return_value = [0.1, 0.2]

    vector_store = MagicMock()
    vector_store.search.return_value = [
        {
            "id": str(chunk_id),
            "score": 0.87,
            "payload": {
                "document_id": str(document_id),
                "content": "asyncio.TaskGroup manages task lifecycles",
                "page_number": 3,
                "section": "Tasks",
            },
        }
    ]

    retriever = DenseRetriever(embedding_provider, vector_store)
    results = retriever.retrieve("what is TaskGroup")

    assert len(results) == 1
    assert results[0].chunk_id == chunk_id
    assert results[0].document_id == document_id
    assert results[0].score == 0.87
    assert results[0].page_number == 3
    assert results[0].section == "Tasks"


def test_dense_retriever_passes_filters_and_top_k() -> None:
    embedding_provider = MagicMock()
    embedding_provider.embed_query.return_value = [0.1]

    vector_store = MagicMock()
    vector_store.search.return_value = []

    retriever = DenseRetriever(embedding_provider, vector_store)
    retriever.retrieve("query", top_k=5, filters={"collection": "python"})

    _, kwargs = vector_store.search.call_args
    assert kwargs["top_k"] == 5
    assert kwargs["filters"] == {"collection": "python"}


def test_dense_retriever_returns_empty_tuple_for_no_results() -> None:
    embedding_provider = MagicMock()
    embedding_provider.embed_query.return_value = [0.1]

    vector_store = MagicMock()
    vector_store.search.return_value = []

    retriever = DenseRetriever(embedding_provider, vector_store)

    assert retriever.retrieve("query") == ()
