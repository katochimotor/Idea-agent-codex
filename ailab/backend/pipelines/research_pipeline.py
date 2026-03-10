from backend.agents.cluster_agent import ClusterAgent
from backend.agents.collector_agent import CollectorAgent
from backend.agents.extractor_agent import ExtractorAgent


class ResearchPipeline:
    def __init__(self) -> None:
        self.collector = CollectorAgent()
        self.extractor = ExtractorAgent()
        self.cluster = ClusterAgent()

    def run(self, stage_callback=None) -> dict:
        if stage_callback:
            stage_callback("collect_documents", "Collecting documents", "Собираем документы из источников.")
        discussions = self.collector.run()
        if stage_callback:
            stage_callback(
                "collect_documents",
                "Collecting documents",
                "Документы собраны из источников.",
                {"documents_scanned": len(discussions)},
            )
        if stage_callback:
            stage_callback("extract_problems", "Extracting problems", "Извлекаем пользовательские проблемы.")
        problems = self.extractor.run(discussions)
        if stage_callback:
            stage_callback(
                "extract_problems",
                "Extracting problems",
                "Проблемы извлечены из обсуждений.",
                {"documents_scanned": len(discussions), "problems_extracted": len(problems)},
            )
        if stage_callback:
            stage_callback("cluster_problems", "Clustering problems", "Группируем проблемы по кластерам.")
        clusters = self.cluster.run(problems)
        if stage_callback:
            stage_callback(
                "cluster_problems",
                "Clustering problems",
                "Проблемы сгруппированы по кластерам.",
                {
                    "documents_scanned": len(discussions),
                    "problems_extracted": len(problems),
                    "clusters_detected": len(clusters),
                },
            )
        return {
            "discussions": discussions,
            "problems": problems,
            "clusters": clusters,
            "metrics": {
                "documents_scanned": len(discussions),
                "problems_extracted": len(problems),
                "clusters_detected": len(clusters),
            },
        }
