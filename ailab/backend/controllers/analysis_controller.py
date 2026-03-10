from datetime import datetime

from sqlmodel import Session, func, select

from backend.models.cluster_model import Problem
from backend.models.idea_model import Idea, IdeaScoreRecord


class AnalysisController:
    def get_summary(self, session: Session) -> dict:
        ideas = session.exec(select(Idea)).all()
        scores = session.exec(select(IdeaScoreRecord.total_score)).all()
        today = datetime.utcnow().date()
        ideas_generated_today = sum(
            1 for idea in ideas if idea.created_at and datetime.fromisoformat(idea.created_at).date() == today
        )

        niche_counts: dict[str, int] = {}
        for idea in ideas:
            niche = idea.niche_label or "General"
            niche_counts[niche] = niche_counts.get(niche, 0) + 1

        top_niches = [name for name, _count in sorted(niche_counts.items(), key=lambda item: item[1], reverse=True)[:3]]
        problems_detected = session.exec(select(func.count()).select_from(Problem)).one()

        return {
            "top_niches": top_niches,
            "average_score": round(sum(scores) / len(scores), 1) if scores else 0.0,
            "ideas_generated_today": ideas_generated_today,
            "problems_detected": problems_detected,
        }
