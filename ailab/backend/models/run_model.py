from __future__ import annotations

from sqlalchemy import CheckConstraint, Index
from sqlmodel import Field, SQLModel


class PipelineRun(SQLModel, table=True):
    __tablename__ = "pipeline_runs"
    __table_args__ = (
        CheckConstraint("status IN ('queued', 'running', 'completed', 'failed', 'cancelled')", name="ck_pipeline_runs_status"),
        CheckConstraint("trigger_type IN ('manual', 'scheduled', 'job', 'system')", name="ck_pipeline_runs_trigger_type"),
        Index("idx_pipeline_runs_type_status", "run_type", "status", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    run_type: str
    status: str
    trigger_type: str
    job_id: int | None = Field(default=None, foreign_key="jobs.id")
    model_registry_entry_id: int | None = Field(default=None, foreign_key="model_registry_entries.id")
    prompt_version_id: int | None = Field(default=None, foreign_key="prompt_versions.id")
    input_summary_json: str | None = None
    output_summary_json: str | None = None
    error_message: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    created_at: str


class RunArtifact(SQLModel, table=True):
    __tablename__ = "run_artifacts"
    __table_args__ = (
        Index("idx_run_artifacts_run_type", "pipeline_run_id", "artifact_type"),
    )

    id: int | None = Field(default=None, primary_key=True)
    pipeline_run_id: int = Field(foreign_key="pipeline_runs.id")
    artifact_type: str
    artifact_ref_type: str
    artifact_ref_id: int
    created_at: str


class ExtractionRun(SQLModel, table=True):
    __tablename__ = "extraction_runs"
    __table_args__ = (
        CheckConstraint("status IN ('running', 'completed', 'failed')", name="ck_extraction_runs_status"),
        Index("idx_extraction_runs_document_id", "document_id", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    pipeline_run_id: int = Field(foreign_key="pipeline_runs.id")
    document_id: int = Field(foreign_key="documents.id")
    extractor_name: str
    extractor_version: str | None = None
    status: str
    output_json: str | None = None
    error_message: str | None = None
    created_at: str
    updated_at: str
