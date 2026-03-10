from __future__ import annotations

from sqlmodel import Session, func, select

from backend.models.cluster_model import ProblemCluster, ProblemClusterMembership
from backend.models.idea_model import Idea
from backend.models.opportunity_model import Opportunity


class OpportunityController:
    def list_opportunities(self, session: Session, limit: int = 6) -> list[dict]:
        rows = session.exec(
            select(Opportunity).order_by(Opportunity.opportunity_score.desc(), Opportunity.created_at.desc()).limit(limit)
        ).all()
        return [self._serialize_opportunity(session, row) for row in rows]

    def get_opportunity_detail(self, session: Session, cluster_id: int) -> dict | None:
        opportunity = session.exec(
            select(Opportunity)
            .where(Opportunity.cluster_id == cluster_id)
            .order_by(Opportunity.created_at.desc(), Opportunity.opportunity_score.desc())
        ).first()
        cluster = session.get(ProblemCluster, cluster_id)
        if not opportunity or not cluster:
            return None

        ideas = session.exec(select(Idea).where(Idea.cluster_id == cluster_id).order_by(Idea.created_at.desc())).all()
        problem_count = session.exec(
            select(func.count()).select_from(ProblemClusterMembership).where(ProblemClusterMembership.cluster_id == cluster_id)
        ).one()
        return {
            **self._serialize_opportunity(session, opportunity),
            "cluster": {
                "id": cluster.id,
                "title": cluster.title,
                "summary": cluster.summary,
                "niche": cluster.niche_label or "General",
                "problem_count": problem_count,
            },
            "related_ideas": [
                {
                    "id": idea.id,
                    "title": idea.title,
                    "summary": idea.summary,
                    "created_at": idea.created_at,
                    "opportunity_score": idea.opportunity_score,
                }
                for idea in ideas
            ],
        }

    def _serialize_opportunity(self, session: Session, row: Opportunity) -> dict:
        cluster = session.get(ProblemCluster, row.cluster_id)
        problem_count = session.exec(
            select(func.count()).select_from(ProblemClusterMembership).where(ProblemClusterMembership.cluster_id == row.cluster_id)
        ).one()
        related_ideas = session.exec(select(func.count()).select_from(Idea).where(Idea.cluster_id == row.cluster_id)).one()
        return {
            "id": row.id,
            "cluster_id": row.cluster_id,
            "title": row.title,
            "description": row.description,
            "opportunity_score": row.opportunity_score,
            "pain_score": row.pain_score,
            "frequency_score": row.frequency_score,
            "solution_gap_score": row.solution_gap_score,
            "market_score": row.market_score,
            "build_complexity_score": row.build_complexity_score,
            "problem_count": problem_count,
            "related_ideas": related_ideas,
            "cluster_summary": cluster.summary if cluster else row.description,
            "cluster_title": cluster.title if cluster else row.title,
        }
