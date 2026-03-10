from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class ModelRegistryEntry(SQLModel, table=True):
    __tablename__ = "model_registry_entries"
    __table_args__ = (
        UniqueConstraint("task_key", "provider", "model_name", name="uq_model_registry_task_provider_model"),
        Index("idx_model_registry_task_default", "task_key", "is_default", "enabled"),
    )

    id: int | None = Field(default=None, primary_key=True)
    task_key: str
    provider: str
    model_name: str
    endpoint_type: str
    input_mode: str
    output_schema_json: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    embedding_dimensions: int | None = None
    is_default: bool = Field(default=False)
    enabled: bool = Field(default=True)
    fallback_model_id: int | None = Field(default=None, foreign_key="model_registry_entries.id")
    config_json: str | None = None
    created_at: str
    updated_at: str


class PromptVersion(SQLModel, table=True):
    __tablename__ = "prompt_versions"
    __table_args__ = (
        UniqueConstraint("prompt_key", "version_label", name="uq_prompt_versions_prompt_version"),
    )

    id: int | None = Field(default=None, primary_key=True)
    prompt_key: str
    version_label: str
    template_text: str
    variables_json: str | None = None
    checksum: str
    created_at: str
