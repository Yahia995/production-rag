from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.postgres import get_db_session
from app.db.qdrant import QdrantVectorStore
from app.embeddings.base import EmbeddingProvider
from app.embeddings.local import LocalEmbeddingProvider
from app.generation.base import LLMProvider
from app.generation.ollama import OllamaProvider
from app.query.transformer import QueryTransformer
from app.rag.pipeline import RagPipeline
from app.reranking.base import Reranker
from app.reranking.cross_encoder import CrossEncoderReranker
from app.retrieval.dense import DenseRetriever
from app.retrieval.sparse import SparseRetriever


async def get_db(
    session: AsyncSession = None,
) -> AsyncGenerator[AsyncSession, None]:
    async for db_session in get_db_session():
        yield db_session


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()

    return LocalEmbeddingProvider(dimension=384 if not settings.embedding_model else 384)


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    embedding_provider = get_embedding_provider()

    return QdrantVectorStore(
        collection_name="chunks",
        vector_size=embedding_provider.dimension,
    )


@lru_cache
def get_dense_retriever() -> DenseRetriever:
    return DenseRetriever(
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
    )


@lru_cache
def get_sparse_retriever() -> SparseRetriever:
    return SparseRetriever()


@lru_cache
def get_reranker() -> Reranker:
    settings = get_settings()

    return CrossEncoderReranker(
        model_name=settings.reranker_model or "cross-encoder/ms-marco-MiniLM-L-6-v2",
    )


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()

    return OllamaProvider(model=settings.llm_model or "llama3")


def get_query_transformer() -> QueryTransformer:
    return QueryTransformer(llm_provider=get_llm_provider())


def get_rag_pipeline() -> RagPipeline:
    return RagPipeline(
        dense_retriever=get_dense_retriever(),
        sparse_retriever=get_sparse_retriever(),
        reranker=get_reranker(),
        llm_provider=get_llm_provider(),
        query_transformer=get_query_transformer(),
    )
