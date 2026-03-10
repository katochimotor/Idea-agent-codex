from sqlmodel import Session, select

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

        return IdeaDetail(
            id=idea.id,
            title=idea.title,
            summary=idea.summary,
            problem="Повторяющаяся пользовательская боль из публичных обсуждений.",
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
            report_path=report.output_path if report else str(settings.reports_dir / f"{slugify(idea.title)}.md"),
        )
