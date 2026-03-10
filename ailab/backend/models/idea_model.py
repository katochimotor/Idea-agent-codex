from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Idea(SQLModel, table=True):
    __tablename__ = "ideas"
    __table_args__ = (
        CheckConstraint("source_type IN ('discussion-derived', 'ai-generated', 'hybrid')", name="ck_ideas_source_type"),
        CheckConstraint("status IN ('active', 'archived', 'rejected')", name="ck_ideas_status"),
        UniqueConstraint("slug", name="uq_ideas_slug"),
        Index("idx_ideas_cluster_id", "cluster_id"),
        Index("idx_ideas_status_created_at", "status", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    cluster_id: int | None = Field(default=None, foreign_key="problem_clusters.id")
    primary_source_document_id: int | None = Field(default=None, foreign_key="documents.id")
    title: str
    slug: str
    summary: str
    target_audience: str | None = None
    niche_label: str | None = None
    source_type: str
    generation_run_id: int | None = Field(default=None, foreign_key="pipeline_runs.id")
    status: str = Field(default="active")
    created_at: str
    updated_at: str


class IdeaScoreRecord(SQLModel, table=True):
    __tablename__ = "idea_scores"
    __table_args__ = (
        Index("idx_idea_scores_idea_id_created_at", "idea_id", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="ideas.id")
    scoring_run_id: int | None = Field(default=None, foreign_key="pipeline_runs.id")
    market_demand_score: float
    competition_score: float
    implementation_difficulty_score: float
    monetization_score: float
    confidence_score: float | None = None
    total_score: float
    rationale_json: str | None = None
    created_at: str


class IdeaEvidence(SQLModel, table=True):
    __tablename__ = "idea_evidence"
    __table_args__ = (
        CheckConstraint("evidence_type IN ('document', 'chunk', 'problem', 'cluster')", name="ck_idea_evidence_type"),
        Index("idx_idea_evidence_idea_id", "idea_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="ideas.id")
    evidence_type: str
    evidence_ref_id: int
    relevance_score: float | None = None
    note: str | None = None
    created_at: str


class Report(SQLModel, table=True):
    __tablename__ = "reports"
    __table_args__ = (
        Index("idx_reports_idea_id", "idea_id", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="ideas.id")
    report_type: str
    output_path: str
    markdown_checksum: str | None = None
    generated_by_run_id: int | None = Field(default=None, foreign_key="pipeline_runs.id")
    created_at: str


class IdeaScore(BaseModel):
    market_demand: int
    competition: int
    difficulty: int
    monetization: int
    total: float


class IdeaDetail(BaseModel):
    id: int
    title: str
    summary: str
    problem: str
    audience: str
    features: list[str]
    tech_stack: list[str]
    score: IdeaScore
    report_path: Optional[str] = None
