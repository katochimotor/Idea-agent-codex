class ClusterAgent:
    def run(self, problems: list[dict]) -> list[dict]:
        clusters = []
        for index, problem in enumerate(problems, start=1):
            clusters.append(
                {
                    **problem,
                    "cluster_id": f"cluster-{index}",
                    "cluster_title": problem.get("thread_title") or problem["problem_statement"][:80],
                    "cluster_summary": problem["problem_statement"],
                    "niche": "AI tools",
                }
            )
        return clusters
