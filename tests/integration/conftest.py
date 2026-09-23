import pytest
import redis
from qdrant_client import QdrantClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models.base import Base


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/production_rag_test",
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def qdrant_client():
    client = QdrantClient(url="http://localhost:6333")

    yield client


@pytest.fixture
def redis_client():
    client = redis.from_url("redis://localhost:6379/1")

    yield client

    client.flushdb()
