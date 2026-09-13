"""Embedding providers."""

from app.embeddings.base import EmbeddingProvider
from app.embeddings.local import LocalEmbeddingProvider

__all__ = [
    "EmbeddingProvider",
    "LocalEmbeddingProvider",
]
