from datetime import datetime

from sqlmodel import Session

from backend.models.project_model import Project, ProjectFile
from backend.settings import settings
from backend.utils.file_writer import write_text_file
from backend.utils.slug_generator import slugify


class ProjectController:
    def create_project(self, session: Session, idea_id: int, title: str) -> dict:
        now = datetime.utcnow().isoformat()
        folder_name = slugify(title)
        project_dir = settings.projects_dir / folder_name
        project_dir.mkdir(parents=True, exist_ok=True)

        files = {
            "README.md": f"# {title}\n\nЛокальный проект, созданный из идеи.\n",
            "architecture.md": "# Архитектура\n\nЧерновой документ архитектуры.\n",
            "tech_stack.md": "# Технологический стек\n\n- FastAPI\n- React\n- SQLite\n",
            "mvp_plan.md": "# MVP план\n\n1. Сбор данных\n2. Анализ\n3. UI\n",
            "starter_prompt.md": "# Starter Prompt\n\nОпиши первую реализацию продукта.\n",
            "run.bat": "@echo off\npython -m http.server 9000\n",
        }
        for name, content in files.items():
            write_text_file(project_dir / name, content)

        project = Project(
            idea_id=idea_id,
            title=title,
            folder_path=str(project_dir),
            status="generated",
            created_by_job_id=None,
            created_at=now,
            updated_at=now,
        )
        session.add(project)
        session.flush()

        for name in files:
            session.add(
                ProjectFile(
                    project_id=project.id,
                    relative_path=name,
                    file_type="script" if name.endswith(".bat") else "markdown",
                    checksum=None,
                    created_at=now,
                    updated_at=now,
                )
            )

        session.commit()
        session.refresh(project)

        return {"id": project.id, "idea_id": idea_id, "folder_path": str(project_dir)}
