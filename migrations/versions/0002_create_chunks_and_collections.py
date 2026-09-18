"""create chunks and collections

Revision ID: 0002_create_chunks_and_collections
Revises: 0001_create_documents
Create Date: 2026-09-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0002_create_chunks_and_collections"
down_revision: Union[str, Sequence[str], None] = "0001_create_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "collections",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "chunks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "document_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_chunks_document_version_id",
        "chunks",
        ["document_version_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_chunks_document_version_id", table_name="chunks")
    op.drop_table("chunks")
    op.drop_table("collections")
