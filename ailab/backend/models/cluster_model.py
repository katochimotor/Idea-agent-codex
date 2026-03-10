from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Problem(SQLModel, table=True):
    __tablename__ = "problems"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'merged', 'discarded')", name="ck_problems_status"),
        Index("idx_problems_document_id", "document_id"),
        Index("idx_problems_status", "status", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    document_id: int | None = Field(default=None, foreign_key="documents.id")
    extraction_run_id: int | None = Field(default=None, foreign_key="extraction_runs.id")
    normalized_text: str
    original_text: str | None = None
    problem_type: str | None = None
    severity_score: float | None = None
    evidence_span_json: str | None = None
    language_code: str = Field(default="en")
    status: str = Field(default="active")
    created_at: str
    updated_at: str


class ProblemCluster(SQLModel, table=True):
    __tablename__ = "problem_clusters"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'merged', 'archived')", name="ck_problem_clusters_status"),
        UniqueConstraint("cluster_key", name="uq_problem_clusters_cluster_key"),
        Index("idx_problem_clusters_niche", "niche_label", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    cluster_key: str
    title: str
    summary: str | None = None
    niche_label: str | None = None
    centroid_vector_key: str | None = None
    status: str = Field(default="active")
    created_by_run_id: int | None = Field(default=None, foreign_key="pipeline_runs.id")
    created_at: str
    updated_at: str


class ProblemClusterMembership(SQLModel, table=True):
    __tablename__ = "problem_cluster_memberships"
    __table_args__ = (
        UniqueConstraint("cluster_id", "problem_id", name="uq_problem_cluster_memberships_cluster_problem"),
        Index("idx_problem_cluster_memberships_problem", "problem_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    cluster_id: int = Field(foreign_key="problem_clusters.id")
    problem_id: int = Field(foreign_key="problems.id")
    membership_score: float | None = None
    assigned_by_run_id: int | None = Field(default=None, foreign_key="pipeline_runs.id")
    created_at: str
