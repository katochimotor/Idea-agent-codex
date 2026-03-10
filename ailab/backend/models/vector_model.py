from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class VectorCollection(SQLModel, table=True):
    __tablename__ = "vector_collections"
    __table_args__ = (
        CheckConstraint("entity_type IN ('document_chunk', 'problem', 'cluster', 'idea')", name="ck_vector_collections_entity_type"),
        UniqueConstraint("collection_key", name="uq_vector_collections_collection_key"),
    )

    id: int | None = Field(default=None, primary_key=True)
    collection_key: str
    entity_type: str
    embedding_model_id: int = Field(foreign_key="model_registry_entries.id")
    dimensions: int
    metric: str = Field(default="cosine")
    index_path: str
    metadata_json: str | None = None
    created_at: str
    updated_at: str


class VectorEntry(SQLModel, table=True):
    __tablename__ = "vector_entries"
    __table_args__ = (
        CheckConstraint("entity_type IN ('document_chunk', 'problem', 'cluster', 'idea')", name="ck_vector_entries_entity_type"),
        UniqueConstraint("collection_id", "entity_type", "entity_id", "version", name="uq_vector_entries_collection_entity_version"),
        UniqueConstraint("vector_key", name="uq_vector_entries_vector_key"),
        Index("idx_vector_entries_collection_entity", "collection_id", "entity_type", "entity_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    collection_id: int = Field(foreign_key="vector_collections.id")
    entity_id: int
    entity_type: str
    vector_key: str
    vector_hash: str | None = None
    version: int = Field(default=1)
    metadata_json: str | None = None
    created_at: str
    updated_at: str


class VectorSyncRun(SQLModel, table=True):
    __tablename__ = "vector_sync_runs"
    __table_args__ = (
        CheckConstraint("status IN ('running', 'completed', 'failed')", name="ck_vector_sync_runs_status"),
    )

    id: int | None = Field(default=None, primary_key=True)
    collection_id: int = Field(foreign_key="vector_collections.id")
    pipeline_run_id: int | None = Field(default=None, foreign_key="pipeline_runs.id")
    status: str
    inserted_count: int = Field(default=0)
    updated_count: int = Field(default=0)
    deleted_count: int = Field(default=0)
    error_message: str | None = None
    created_at: str
    updated_at: str
