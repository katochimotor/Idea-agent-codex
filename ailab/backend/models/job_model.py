from __future__ import annotations

from sqlalchemy import CheckConstraint, Index
from sqlmodel import Field, SQLModel


class Job(SQLModel, table=True):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed', 'cancelled', 'retrying')",
            name="ck_jobs_status",
        ),
        Index("idx_jobs_status_priority", "status", "priority", "created_at"),
        Index("idx_jobs_job_type", "job_type", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    job_type: str
    status: str
    priority: int = Field(default=100)
    requested_by: str | None = None
    parent_job_id: int | None = Field(default=None, foreign_key="jobs.id")
    payload_json: str | None = None
    result_json: str | None = None
    error_message: str | None = None
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    scheduled_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    created_at: str
    updated_at: str


class JobEvent(SQLModel, table=True):
    __tablename__ = "job_events"
    __table_args__ = (
        Index("idx_job_events_job_id_created_at", "job_id", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="jobs.id")
    event_type: str
    status: str | None = None
    message: str | None = None
    payload_json: str | None = None
    created_at: str
