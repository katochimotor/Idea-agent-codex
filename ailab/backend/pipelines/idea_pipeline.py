from backend.agents.idea_generator_agent import IdeaGeneratorAgent
from backend.pipelines.research_pipeline import ResearchPipeline
from backend.pipelines.scoring_pipeline import ScoringPipeline


class IdeaPipeline:
    def __init__(self) -> None:
        self.research = ResearchPipeline()
        self.generator = IdeaGeneratorAgent()
        self.scoring = ScoringPipeline()

    def run(self) -> list[dict]:
        clusters = self.research.run()
        ideas = self.generator.run(clusters)
        return self.scoring.run(ideas)
