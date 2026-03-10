from datetime import datetime
from pathlib import Path

from sqlmodel import Session, select

from backend.agents.report_agent import ReportAgent
from backend.models.document_model import Document
from backend.models.idea_model import Idea, IdeaDetail, IdeaScore, IdeaScoreRecord, Report
from backend.models.source_model import Source
from backend.services.pipeline_orchestration_service import PipelineOrchestrationService
from backend.settings import settings
from backend.utils.idea_formatter import idea_to_card
from backend.utils.slug_generator import slugify


class IdeaController:
    def __init__(self) -> None:
        self.orchestration = PipelineOrchestrationService()
        self.report_agent = ReportAgent()

    def _latest_score(self, session: Session, idea_id: int) -> IdeaScoreRecord | None:
        return session.exec(
            select(IdeaScoreRecord)
            .where(IdeaScoreRecord.idea_id == idea_id)
            .order_by(IdeaScoreRecord.created_at.desc())
        ).first()

    def _source_label(self, session: Session, idea: Idea) -> str:
        if idea.primary_source_document_id:
            document = session.get(Document, idea.primary_source_document_id)
            if document:
                source = session.get(Source, document.source_id)
                if source:
                    return source.display_name
        return idea.source_type

    def _build_card(self, session: Session, idea: Idea) -> dict:
        score = self._latest_score(session, idea.id)
        total_score = score.total_score if score else 0.0
        return idea_to_card(
            idea,
            score=total_score,
            source=self._source_label(session, idea),
        )

    def _build_problem_text(self, session: Session, idea: Idea) -> str:
        if idea.primary_source_document_id:
            document = session.get(Document, idea.primary_source_document_id)
            if document:
                return document.content_markdown or document.content_text or idea.summary
        return idea.summary

    def _resolve_report_path(self, output_path: str | None, idea: Idea) -> Path:
        if output_path:
            path = Path(output_path)
            if path.is_absolute():
                return path
            return (settings.runtime_dir / path).resolve()
        return (settings.reports_dir / f"{slugify(idea.title)}.md").resolve()

    def _ensure_report(self, session: Session, idea: Idea, report: Report | None) -> tuple[str, str]:
        problem = self._build_problem_text(session, idea)
        needs_commit = False
        report_path = self._resolve_report_path(report.output_path if report else None, idea)

        if not report_path.exists():
            generated_path = self.report_agent.run(
                settings.reports_dir,
                {"title": idea.title, "problem": problem, "summary": idea.summary},
            ).resolve()
            report_path = generated_path
            if report:
                report.output_path = str(report_path)
            else:
                session.add(
                    Report(
                        idea_id=idea.id,
                        report_type="markdown",
                        output_path=str(report_path),
                        markdown_checksum=None,
                        generated_by_run_id=idea.generation_run_id,
                        created_at=datetime.utcnow().isoformat(),
                    )
                )
            needs_commit = True
        elif report and report.output_path != str(report_path):
            report.output_path = str(report_path)
            needs_commit = True

        if needs_commit:
            session.commit()

        return str(report_path), report_path.read_text(encoding="utf-8")

    def list_ideas(self, session: Session) -> list[dict]:
        ideas = session.exec(select(Idea).order_by(Idea.created_at.desc())).all()
        cards = [self._build_card(session, idea) for idea in ideas]
        return sorted(cards, key=lambda item: item["score"], reverse=True)

    def discover_ideas(self, session: Session) -> list[dict]:
        result = self.orchestration.discover_and_persist(session, trigger_type="manual", requested_by="dashboard")
        return [self._build_card(session, session.get(Idea, item["id"])) for item in result["ideas"]]

    def get_idea(self, session: Session, idea_id: int) -> IdeaDetail | None:
        idea = session.get(Idea, idea_id)
        if not idea:
            return None

        score_record = self._latest_score(session, idea.id)
        report = session.exec(
            select(Report).where(Report.idea_id == idea.id).order_by(Report.created_at.desc())
        ).first()
        report_path, report_content = self._ensure_report(session, idea, report)
        problem = self._build_problem_text(session, idea)

        return IdeaDetail(
            id=idea.id,
            title=idea.title,
            summary=idea.summary,
            problem=problem,
            audience=idea.target_audience or "Solo founders, indie developers",
            features=[
                "Сбор обсуждений",
                "Извлечение проблем",
                "Оценка идеи",
            ],
            tech_stack=["FastAPI", "React", "SQLite"],
            score=IdeaScore(
                market_demand=int(score_record.market_demand_score if score_record else 0),
                competition=int(score_record.competition_score if score_record else 0),
                difficulty=int(score_record.implementation_difficulty_score if score_record else 0),
                monetization=int(score_record.monetization_score if score_record else 0),
                total=score_record.total_score if score_record else 0.0,
            ),
            report_path=report_path,
            report_content=report_content,
        )
