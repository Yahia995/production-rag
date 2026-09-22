from app.api.dependencies import (
    get_dense_retriever,
    get_embedding_provider,
    get_llm_provider,
    get_rag_pipeline,
    get_reranker,
    get_sparse_retriever,
    get_vector_store,
)
from app.generation.ollama import OllamaProvider
from app.reranking.cross_encoder import CrossEncoderReranker
from app.retrieval.dense import DenseRetriever
from app.retrieval.sparse import SparseRetriever


def test_get_embedding_provider_is_cached() -> None:
    assert get_embedding_provider() is get_embedding_provider()


def test_get_vector_store_uses_embedding_dimension() -> None:
    vector_store = get_vector_store()
    embedding_provider = get_embedding_provider()

    assert vector_store.vector_size == embedding_provider.dimension


def test_get_dense_retriever_returns_dense_retriever() -> None:
    assert isinstance(get_dense_retriever(), DenseRetriever)


def test_get_sparse_retriever_returns_sparse_retriever() -> None:
    assert isinstance(get_sparse_retriever(), SparseRetriever)


def test_get_reranker_returns_cross_encoder_reranker() -> None:
    assert isinstance(get_reranker(), CrossEncoderReranker)


def test_get_llm_provider_returns_ollama_provider() -> None:
    assert isinstance(get_llm_provider(), OllamaProvider)


def test_get_rag_pipeline_wires_all_components() -> None:
    pipeline = get_rag_pipeline()

    assert pipeline.dense_retriever is get_dense_retriever()
    assert pipeline.sparse_retriever is get_sparse_retriever()
    assert pipeline.query_transformer is not None
