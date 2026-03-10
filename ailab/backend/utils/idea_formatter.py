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
    difficulty: str = "Средняя",
    monetization: str = "Подписка",
    tags: list[str] | None = None,
) -> dict:
    return {
        "id": idea.id,
        "title": idea.title,
        "summary": idea.summary,
        "score": round(score, 1),
        "niche": idea.niche_label or "General",
        "source": source,
        "difficulty": difficulty,
        "monetization": monetization,
        "tags": tags or _default_tags(idea),
    }
