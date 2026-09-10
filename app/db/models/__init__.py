"""Database models."""

from app.db.models.base import Base
from app.db.models.documents import Document, DocumentVersion

__all__ = [
    "Base",
    "Document",
    "DocumentVersion",
]
