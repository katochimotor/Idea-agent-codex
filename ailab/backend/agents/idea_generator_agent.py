from backend.ai.llm_client import LLMClient
from backend.services.prompt_builder import build_idea_prompt


class IdeaGeneratorAgent:
    def __init__(self) -> None:
        self.client = LLMClient()

    def run(self, clusters: list[dict]) -> list[dict]:
        ideas = []
        for cluster in clusters:
            response = self.client.generate_idea(build_idea_prompt(cluster["problem_statement"], cluster["niche"]))
            ideas.append(
                {
                    "title": response["title"],
                    "summary": response["summary"],
                    "problem": cluster["problem_statement"],
                    "audience": response["audience"],
                    "niche": cluster["niche"],
                    "source": cluster["source"],
                }
            )
        return ideas
