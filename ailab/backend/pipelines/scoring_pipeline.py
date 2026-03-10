from backend.agents.idea_scoring_agent import IdeaScoringAgent


class ScoringPipeline:
    def __init__(self) -> None:
        self.agent = IdeaScoringAgent()

    def run(self, ideas: list[dict]) -> list[dict]:
        return self.agent.run(ideas)
