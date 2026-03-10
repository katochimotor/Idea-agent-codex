from backend.agents.cluster_agent import ClusterAgent
from backend.agents.collector_agent import CollectorAgent
from backend.agents.extractor_agent import ExtractorAgent


class ResearchPipeline:
    def __init__(self) -> None:
        self.collector = CollectorAgent()
        self.extractor = ExtractorAgent()
        self.cluster = ClusterAgent()

    def run(self, stage_callback=None) -> list[dict]:
        if stage_callback:
            stage_callback("collect_documents", "Collecting documents", "Собираем документы из источников.")
        discussions = self.collector.run()
        if stage_callback:
            stage_callback("extract_problems", "Extracting problems", "Извлекаем пользовательские проблемы.")
        problems = self.extractor.run(discussions)
        if stage_callback:
            stage_callback("cluster_problems", "Clustering problems", "Группируем проблемы по кластерам.")
        return self.cluster.run(problems)
