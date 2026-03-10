from backend.agents.cluster_agent import ClusterAgent
from backend.agents.collector_agent import CollectorAgent
from backend.agents.extractor_agent import ExtractorAgent


class ResearchPipeline:
    def __init__(self) -> None:
        self.collector = CollectorAgent()
        self.extractor = ExtractorAgent()
        self.cluster = ClusterAgent()

    def run(self) -> list[dict]:
        discussions = self.collector.run()
        problems = self.extractor.run(discussions)
        return self.cluster.run(problems)
