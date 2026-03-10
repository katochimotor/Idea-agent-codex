from backend.agents.idea_generator_agent import IdeaGeneratorAgent
from backend.pipelines.research_pipeline import ResearchPipeline
from backend.pipelines.scoring_pipeline import ScoringPipeline


class IdeaPipeline:
    def __init__(self) -> None:
        self.research = ResearchPipeline()
        self.generator = IdeaGeneratorAgent()
        self.scoring = ScoringPipeline()

    def run(self, stage_callback=None) -> list[dict]:
        clusters = self.research.run(stage_callback=stage_callback)
        if stage_callback:
            stage_callback("generate_ideas", "Generating ideas", "Генерируем идеи из найденных кластеров.")
        ideas = self.generator.run(clusters)
        if stage_callback:
            stage_callback("score_ideas", "Scoring ideas", "Оцениваем идеи по ключевым метрикам.")
        return self.scoring.run(ideas)
