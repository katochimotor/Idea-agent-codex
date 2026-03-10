from backend.models.idea_model import Idea


def _default_tags(idea: Idea) -> list[str]:
    tags = []
    if idea.niche_label:
        tags.extend(part.lower() for part in idea.niche_label.split())
    tags.append(idea.source_type)
    return tags[:4]


def idea_to_card(
    idea: Idea,
    *,
    score: float,
    source: str,
    problem: str | None = None,
    audience: str | None = None,
    source_url: str | None = None,
    source_title: str | None = None,
    source_quote: str | None = None,
    difficulty: str = "Средняя",
    monetization: str = "Подписка",
    tags: list[str] | None = None,
) -> dict:
    return {
        "id": idea.id,
        "title": idea.title,
        "summary": idea.summary,
        "problem": problem or idea.summary,
        "audience": audience or idea.target_audience or "Solo founders, indie developers",
        "score": round(score, 1),
        "niche": idea.niche_label or "General",
        "source": source,
        "source_url": source_url,
        "source_title": source_title,
        "source_quote": source_quote,
        "difficulty": difficulty,
        "monetization": monetization,
        "tags": tags or _default_tags(idea),
        "cluster_id": idea.cluster_id,
        "opportunity_score": idea.opportunity_score,
        "status": idea.status,
        "created_at": idea.created_at,
    }
