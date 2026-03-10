import json

from sqlmodel import Session, func, select

from backend.controllers.idea_controller import IdeaController
from backend.models.cluster_model import ProblemCluster, ProblemClusterMembership
from backend.models.idea_model import Idea
from backend.models.job_model import Job, JobEvent
from backend.models.opportunity_model import Opportunity


class DashboardController:
    def __init__(self) -> None:
        self.idea_controller = IdeaController()

    def get_dashboard(self, session: Session) -> dict:
        latest_job = session.exec(
            select(Job).where(Job.job_type == "discover_ideas").order_by(Job.created_at.desc())
        ).first()
        latest_result_ideas = self._latest_result_ideas(session, latest_job)
        top_opportunities = self._top_opportunities(session)
        latest_events = self._latest_events(session, latest_job.id if latest_job else None)
        trends = [item["cluster_title"] for item in top_opportunities[:4]] or ["AI tools", "developer tools", "automation"]

        return {
            "hero_title": "AI Idea Research Lab",
            "hero_subtitle": "Локальная исследовательская среда для поиска повторяющихся проблем и продуктовых возможностей.",
            "trends": trends,
            "latest_pipeline_run": self._serialize_job(latest_job),
            "latest_pipeline_events": latest_events,
            "latest_results": latest_result_ideas,
            "top_opportunities": top_opportunities,
            "discovery_insights": self._discovery_insights(session),
        }

    def _latest_result_ideas(self, session: Session, latest_job: Job | None) -> list[dict]:
        if latest_job and latest_job.result_json:
            payload = json.loads(latest_job.result_json)
            idea_ids = payload.get("idea_ids") or []
            ideas = []
            for idea_id in idea_ids:
                idea = session.get(Idea, idea_id)
                if idea and idea.status == "active":
                    ideas.append(self.idea_controller._build_card(session, idea))
            if ideas:
                return ideas

        fallback = session.exec(
            select(Idea).where(Idea.status == "active").order_by(Idea.created_at.desc())
        ).all()
        return [self.idea_controller._build_card(session, idea) for idea in fallback[:6]]

    def _top_opportunities(self, session: Session) -> list[dict]:
        rows = session.exec(
            select(Opportunity).order_by(Opportunity.opportunity_score.desc(), Opportunity.created_at.desc()).limit(6)
        ).all()
        payload = []
        for row in rows:
            problem_count = session.exec(
                select(func.count()).select_from(ProblemClusterMembership).where(ProblemClusterMembership.cluster_id == row.cluster_id)
            ).one()
            related_ideas = session.exec(
                select(func.count()).select_from(Idea).where(Idea.cluster_id == row.cluster_id).where(Idea.status == "active")
            ).one()
            cluster = session.get(ProblemCluster, row.cluster_id)
            payload.append(
                {
                    "cluster_id": row.cluster_id,
                    "title": row.title,
                    "description": row.description,
                    "opportunity_score": row.opportunity_score,
                    "problem_count": problem_count,
                    "related_ideas": related_ideas,
                    "cluster_title": cluster.title if cluster else row.title,
                    "cluster_summary": cluster.summary if cluster else row.description,
                }
            )
        return payload

    def _latest_events(self, session: Session, job_id: int | None) -> list[dict]:
        if not job_id:
            return []
        rows = session.exec(select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.created_at.asc())).all()
        return [
            {
                "id": row.id,
                "event_type": row.event_type,
                "status": row.status,
                "message": row.message,
                "payload": json.loads(row.payload_json) if row.payload_json else None,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    def _serialize_job(self, job: Job | None) -> dict | None:
        if not job:
            return None
        result = json.loads(job.result_json) if job.result_json else {}
        return {
            "id": job.id,
            "status": job.status,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "error_message": job.error_message,
            "pipeline_metrics": result.get("pipeline_metrics") or {},
        }

    def _discovery_insights(self, session: Session) -> list[dict]:
        active_ideas = session.exec(select(Idea).where(Idea.status == "active")).all()
        source_counts: dict[str, int] = {}
        for idea in active_ideas:
            label = self.idea_controller._source_label(session, idea)
            source_counts[label] = source_counts.get(label, 0) + 1
        return [
            {"label": source, "value": count}
            for source, count in sorted(source_counts.items(), key=lambda item: item[1], reverse=True)[:4]
        ]
