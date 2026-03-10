from __future__ import annotations

from sqlmodel import Field, SQLModel


class Opportunity(SQLModel, table=True):
    __tablename__ = "opportunities"

    id: int | None = Field(default=None, primary_key=True)
    cluster_id: int = Field(foreign_key="problem_clusters.id")
    title: str
    description: str
    pain_score: float
    frequency_score: float
    solution_gap_score: float
    market_score: float
    build_complexity_score: float
    opportunity_score: float
    created_at: str
