from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    __tablename__ = "sources"
    __table_args__ = (
        UniqueConstraint("source_key", name="uq_sources_source_key"),
    )

    id: int | None = Field(default=None, primary_key=True)
    source_key: str
    display_name: str
    source_type: str
    base_url: str | None = None
    enabled: bool = Field(default=True)
    config_json: str | None = None
    created_at: str
    updated_at: str


class SourceCheckpoint(SQLModel, table=True):
    __tablename__ = "source_checkpoints"
    __table_args__ = (
        CheckConstraint("status IN ('idle', 'running', 'completed', 'failed')", name="ck_source_checkpoints_status"),
        UniqueConstraint("source_id", name="uq_source_checkpoints_source_id"),
        Index("idx_source_checkpoints_source_id", "source_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="sources.id")
    cursor_value: str | None = None
    cursor_type: str | None = None
    last_document_published_at: str | None = None
    status: str = Field(default="idle")
    last_run_id: int | None = Field(default=None, foreign_key="pipeline_runs.id")
    last_error: str | None = None
    updated_at: str
