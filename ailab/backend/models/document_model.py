from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Document(SQLModel, table=True):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'duplicate', 'deleted', 'filtered')", name="ck_documents_status"),
        UniqueConstraint("canonical_url", name="uq_documents_canonical_url"),
        UniqueConstraint("source_id", "external_id", name="uq_documents_source_external_id"),
        Index("idx_documents_source_published_at", "source_id", "published_at"),
        Index("idx_documents_content_hash", "content_hash"),
    )

    id: int | None = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="sources.id")
    external_id: str | None = None
    canonical_url: str
    author_name: str | None = None
    title: str | None = None
    language_code: str = Field(default="en")
    published_at: str | None = None
    ingested_at: str
    content_hash: str
    raw_payload_path: str | None = None
    normalized_payload_path: str | None = None
    content_text: str
    content_markdown: str | None = None
    metadata_json: str | None = None
    status: str = Field(default="active")


class DocumentFingerprint(SQLModel, table=True):
    __tablename__ = "document_fingerprints"
    __table_args__ = (
        UniqueConstraint("fingerprint_type", "fingerprint_value", name="uq_document_fingerprints_type_value"),
    )

    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id")
    fingerprint_type: str
    fingerprint_value: str
    created_at: str


class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunks_document_chunk"),
        Index("idx_document_chunks_content_hash", "content_hash"),
    )

    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id")
    chunk_index: int
    chunk_text: str
    token_count: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    content_hash: str
    metadata_json: str | None = None
    created_at: str
