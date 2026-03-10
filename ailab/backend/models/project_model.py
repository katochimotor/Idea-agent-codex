from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint("status IN ('generated', 'updated', 'archived')", name="ck_projects_status"),
        Index("idx_projects_idea_id", "idea_id", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="ideas.id")
    title: str
    folder_path: str
    status: str = Field(default="generated")
    created_by_job_id: int | None = Field(default=None, foreign_key="jobs.id")
    created_at: str
    updated_at: str


class ProjectFile(SQLModel, table=True):
    __tablename__ = "project_files"
    __table_args__ = (
        UniqueConstraint("project_id", "relative_path", name="uq_project_files_project_path"),
    )

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    relative_path: str
    file_type: str
    checksum: str | None = None
    created_at: str
    updated_at: str
