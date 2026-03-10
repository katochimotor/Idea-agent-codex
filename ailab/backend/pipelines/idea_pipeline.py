from backend.agents.idea_generator_agent import IdeaGeneratorAgent
from backend.pipelines.research_pipeline import ResearchPipeline
from backend.pipelines.scoring_pipeline import ScoringPipeline


class IdeaPipeline:
    def __init__(self) -> None:
        self.research = ResearchPipeline()
        self.generator = IdeaGeneratorAgent()
        self.scoring = ScoringPipeline()

    def run_research(self, stage_callback=None) -> dict:
        return self.research.run(stage_callback=stage_callback)

    def generate_and_score(self, clusters: list[dict], stage_callback=None) -> list[dict]:
        if stage_callback:
            stage_callback("generate_ideas", "Generating ideas", "Генерируем идеи из найденных кластеров.")
        ideas = self.generator.run(clusters)
        if stage_callback:
            stage_callback(
                "generate_ideas",
                "Generating ideas",
                "Идеи сгенерированы из opportunity-кластеров.",
                {"ideas_generated": len(ideas)},
            )
        if stage_callback:
            stage_callback("score_ideas", "Scoring ideas", "Оцениваем идеи по ключевым метрикам.")
        scored = self.scoring.run(ideas)
        if stage_callback:
            stage_callback(
                "score_ideas",
                "Scoring ideas",
                "Оценка идей завершена.",
                {"ideas_generated": len(ideas), "ideas_scored": len(scored)},
            )
        return scored

    def run(self, stage_callback=None) -> dict:
        research = self.run_research(stage_callback=stage_callback)
        ideas = self.generate_and_score(research["clusters"], stage_callback=stage_callback)
        return {
            "research": research,
            "ideas": ideas,
            "metrics": {
                **research["metrics"],
                "ideas_generated": len(ideas),
            },
        }
