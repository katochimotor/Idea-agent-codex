class ClusterAgent:
    def run(self, problems: list[dict]) -> list[dict]:
        clusters = []
        for index, problem in enumerate(problems, start=1):
            clusters.append({**problem, "cluster_id": f"cluster-{index}", "niche": "AI tools"})
        return clusters
