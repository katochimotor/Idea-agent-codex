from sqlmodel import Session, select

from backend.models.idea_model import Idea


class DashboardController:
    def get_dashboard(self, session: Session) -> dict:
        ideas = session.exec(select(Idea).order_by(Idea.created_at.desc())).all()
        trends = []
        seen = set()
        for idea in ideas:
            niche = idea.niche_label or "General"
            if niche in seen:
                continue
            seen.add(niche)
            trends.append(niche)
            if len(trends) == 4:
                break

        if not trends:
            trends = ["AI tools", "developer tools", "automation", "productivity"]

        return {
            "hero_title": "Лаборатория идей",
            "hero_subtitle": "Локальный центр исследования проблем, ниш и продуктовых гипотез.",
            "trends": trends,
        }
