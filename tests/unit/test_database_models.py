from app.db.models import Base, Document, DocumentVersion


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
