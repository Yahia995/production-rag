from app.db.models import Base, Document, DocumentVersion, Chunk, Collection, Conversation, Message


def test_document_table_name() -> None:
    assert Document.__tablename__ == "documents"


def test_document_version_table_name() -> None:
    assert DocumentVersion.__tablename__ == "document_versions"


def test_document_columns() -> None:
    columns = set(Document.__table__.columns.keys())

    assert columns == {
        "id",
        "source",
        "title",
        "document_type",
        "collection",
        "created_at",
        "updated_at",
    }


def test_document_version_columns() -> None:
    columns = set(DocumentVersion.__table__.columns.keys())

    assert columns == {
        "id",
        "document_id",
        "version",
        "content_hash",
        "content",
        "created_at",
    }


def test_document_version_has_document_foreign_key() -> None:
    foreign_keys = DocumentVersion.__table__.c.document_id.foreign_keys

    assert len(foreign_keys) == 1

    foreign_key = next(iter(foreign_keys))

    assert foreign_key.target_fullname == "documents.id"


def test_models_are_registered_with_base() -> None:
    tables = set(Base.metadata.tables.keys())

    assert "documents" in tables
    assert "document_versions" in tables

def test_collection_table_name() -> None:
    assert Collection.__tablename__ == "collections"


def test_chunk_table_name() -> None:
    assert Chunk.__tablename__ == "chunks"


def test_chunk_columns() -> None:
    columns = set(Chunk.__table__.columns.keys())

    assert columns == {
        "id",
        "document_version_id",
        "chunk_index",
        "content",
        "page_number",
        "section",
        "created_at",
    }


def test_chunk_has_document_version_foreign_key() -> None:
    foreign_keys = Chunk.__table__.c.document_version_id.foreign_keys

    assert len(foreign_keys) == 1

    foreign_key = next(iter(foreign_keys))

    assert foreign_key.target_fullname == "document_versions.id"


def test_conversation_table_name() -> None:
    assert Conversation.__tablename__ == "conversations"


def test_message_table_name() -> None:
    assert Message.__tablename__ == "messages"


def test_message_columns() -> None:
    columns = set(Message.__table__.columns.keys())

    assert columns == {
        "id",
        "conversation_id",
        "role",
        "content",
        "created_at",
    }


def test_message_has_conversation_foreign_key() -> None:
    foreign_keys = Message.__table__.c.conversation_id.foreign_keys

    assert len(foreign_keys) == 1

    foreign_key = next(iter(foreign_keys))

    assert foreign_key.target_fullname == "conversations.id"
