import pytest
from qdrant_client import QdrantClient

from app.db.qdrant import QdrantVectorStore
from app.embeddings.local import LocalEmbeddingProvider
from app.retrieval.dense import DenseRetriever
from app.retrieval.sparse import SparseRetriever


@pytest.fixture
def qdrant_client() -> QdrantClient:
    client = QdrantClient(url="http://localhost:6333")

    yield client


@pytest.fixture
def embedding_provider() -> LocalEmbeddingProvider:
    return LocalEmbeddingProvider(dimension=64)


@pytest.fixture
def vector_store(qdrant_client, embedding_provider) -> QdrantVectorStore:
    store = QdrantVectorStore(
        collection_name="e2e_test_chunks",
        vector_size=embedding_provider.dimension,
        client=qdrant_client,
    )
    store.ensure_collection()

    yield store

    qdrant_client.delete_collection("e2e_test_chunks")


@pytest.fixture
def dense_retriever(embedding_provider, vector_store) -> DenseRetriever:
    return DenseRetriever(embedding_provider=embedding_provider, vector_store=vector_store)


@pytest.fixture
def sparse_retriever() -> SparseRetriever:
    return SparseRetriever()
