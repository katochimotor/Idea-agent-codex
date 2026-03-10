from backend.utils.score_calculator import calculate_score


class IdeaScoringAgent:
    def run(self, ideas: list[dict]) -> list[dict]:
        scored = []
        for idea in ideas:
            score = calculate_score(8, 6, 5, 8)
            scored.append(
                {
                    **idea,
                    "market_demand": 8,
                    "competition": 6,
                    "difficulty_score": 5,
                    "monetization_score": 8,
                    "score": score,
                    "difficulty": "Средняя",
                    "monetization": "Подписка",
                    "tags": ["ai", "research", "saas"],
                }
            )
        return scored
