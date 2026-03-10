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

    def _source_document(self, session: Session, idea: Idea) -> Document | None:
        if not idea.primary_source_document_id:
            return None
        return session.get(Document, idea.primary_source_document_id)

    def _source_label(self, session: Session, idea: Idea) -> str:
        document = self._source_document(session, idea)
        if document:
            source = session.get(Source, document.source_id)
            if source:
                return source.display_name
        return idea.source_type

    def _source_payload(self, session: Session, idea: Idea) -> dict:
        document = self._source_document(session, idea)
        if not document:
            return {
                "problem": idea.summary,
                "source_url": None,
                "source_title": None,
                "source_quote": None,
            }
        return {
            "problem": document.content_markdown or document.content_text or idea.summary,
            "source_url": document.canonical_url,
            "source_title": document.title,
            "source_quote": document.content_text,
        }

    def _build_card(self, session: Session, idea: Idea) -> dict:
        score = self._latest_score(session, idea.id)
        total_score = score.total_score if score else 0.0
        source_payload = self._source_payload(session, idea)
        return idea_to_card(
            idea,
            score=total_score,
            source=self._source_label(session, idea),
            problem=source_payload["problem"],
            audience=idea.target_audience,
            source_url=source_payload["source_url"],
            source_title=source_payload["source_title"],
            source_quote=source_payload["source_quote"],
        )

    def _build_problem_text(self, session: Session, idea: Idea) -> str:
        source_payload = self._source_payload(session, idea)
        return source_payload["problem"] or idea.summary

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

    def list_ideas(
        self,
        session: Session,
        *,
        sort_by: str = "score",
        order: str = "desc",
        topic: str | None = None,
        source: str | None = None,
        search: str | None = None,
        include_archived: bool = False,
    ) -> list[dict]:
        ideas = session.exec(select(Idea).order_by(Idea.created_at.desc())).all()
        cards = [self._build_card(session, idea) for idea in ideas]

        if not include_archived:
            cards = [card for card in cards if card["status"] == "active"]
        else:
            cards = [card for card in cards if card["status"] != "rejected"]

        if topic:
            topic_lower = topic.lower()
            cards = [card for card in cards if topic_lower in (card["niche"] or "").lower()]
        if source:
            source_lower = source.lower()
            cards = [card for card in cards if source_lower in (card["source"] or "").lower()]
        if search:
            query = search.lower()
            cards = [
                card
                for card in cards
                if query in " ".join(
                    [
                        str(card.get("title") or ""),
                        str(card.get("summary") or ""),
                        str(card.get("problem") or ""),
                        str(card.get("audience") or ""),
                        str(card.get("source_title") or ""),
                        str(card.get("source_quote") or ""),
                    ]
                ).lower()
            ]

        reverse = order != "asc"
        if sort_by == "date":
            cards = sorted(cards, key=lambda item: item["created_at"] or "", reverse=reverse)
        else:
            cards = sorted(cards, key=lambda item: item["score"], reverse=reverse)
        return cards

    def discover_ideas(self, session: Session) -> list[dict]:
        result = self.orchestration.discover_and_persist(session, trigger_type="manual", requested_by="dashboard")
        return [self._build_card(session, session.get(Idea, item["id"])) for item in result["ideas"]]

    def set_status(self, session: Session, idea_id: int, status: str) -> dict | None:
        idea = session.get(Idea, idea_id)
        if not idea:
            return None
        idea.status = status
        idea.updated_at = datetime.utcnow().isoformat()
        session.add(idea)
        session.commit()
        session.refresh(idea)
        return {"id": idea.id, "status": idea.status}

    def get_idea(self, session: Session, idea_id: int) -> IdeaDetail | None:
        idea = session.get(Idea, idea_id)
        if not idea or idea.status == "rejected":
            return None

        score_record = self._latest_score(session, idea.id)
        report = session.exec(
            select(Report).where(Report.idea_id == idea.id).order_by(Report.created_at.desc())
        ).first()
        report_path, report_content = self._ensure_report(session, idea, report)
        source_payload = self._source_payload(session, idea)

        return IdeaDetail(
            id=idea.id,
            title=idea.title,
            summary=idea.summary,
            problem=source_payload["problem"],
            audience=idea.target_audience or "Solo founders, indie developers",
            features=[
                "Сбор обсуждений",
                "Извлечение проблем",
                "Opportunity analysis",
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
            source=self._source_label(session, idea),
            source_url=source_payload["source_url"],
            source_title=source_payload["source_title"],
            source_quote=source_payload["source_quote"],
            cluster_id=idea.cluster_id,
            opportunity_score=idea.opportunity_score,
            report_path=report_path,
            report_content=report_content,
        )
