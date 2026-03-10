from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, delete

from backend.models.opportunity_model import Opportunity


def _clamp_score(value: float) -> float:
    return round(max(1.0, min(10.0, value)), 1)


class OpportunityEngine:
    WEIGHTS = {
        "pain_score": 0.25,
        "frequency_score": 0.20,
        "solution_gap_score": 0.25,
        "market_score": 0.15,
        "build_complexity_score": 0.15,
    }

    PAIN_KEYWORDS = ("waste", "pain", "struggle", "hours", "manual", "lost", "better way", "не могут", "теряют")
    GAP_KEYWORDS = ("manual", "between tools", "no", "can't", "неудобно", "ручн", "теряют", "нет")
    MARKET_KEYWORDS = ("ai", "automation", "support", "developer", "prompt", "workflow", "productivity")
    COMPLEXITY_KEYWORDS = ("platform", "integrat", "sync", "cross", "pipeline", "multi", "distributed")

    def _pain_score(self, text: str) -> float:
        lowered = text.lower()
        keyword_hits = sum(1 for keyword in self.PAIN_KEYWORDS if keyword in lowered)
        intensity = 4.5 + keyword_hits * 1.2 + min(len(text) / 140.0, 2.0)
        return _clamp_score(intensity)

    def _frequency_score(self, problem_count: int) -> float:
        return _clamp_score(3.5 + problem_count * 1.8)

    def _solution_gap_score(self, text: str) -> float:
        lowered = text.lower()
        keyword_hits = sum(1 for keyword in self.GAP_KEYWORDS if keyword in lowered)
        return _clamp_score(4.0 + keyword_hits * 1.4)

    def _market_score(self, niche: str, text: str) -> float:
        lowered = f"{niche} {text}".lower()
        keyword_hits = sum(1 for keyword in self.MARKET_KEYWORDS if keyword in lowered)
        return _clamp_score(5.0 + keyword_hits * 0.9)

    def _build_complexity_score(self, text: str) -> float:
        lowered = text.lower()
        complexity_hits = sum(1 for keyword in self.COMPLEXITY_KEYWORDS if keyword in lowered)
        return _clamp_score(8.5 - complexity_hits * 1.1)

    def _final_score(self, *, pain_score: float, frequency_score: float, solution_gap_score: float, market_score: float, build_complexity_score: float) -> float:
        return round(
            pain_score * self.WEIGHTS["pain_score"]
            + frequency_score * self.WEIGHTS["frequency_score"]
            + solution_gap_score * self.WEIGHTS["solution_gap_score"]
            + market_score * self.WEIGHTS["market_score"]
            + build_complexity_score * self.WEIGHTS["build_complexity_score"],
            2,
        )

    def analyze_clusters(self, session: Session, clusters: list[dict]) -> dict:
        session.exec(delete(Opportunity))
        session.flush()

        now = datetime.utcnow().isoformat()
        discovered: list[dict] = []

        for cluster in clusters:
            text = cluster.get("summary") or cluster.get("title") or cluster.get("problem_statement") or ""
            niche = cluster.get("niche") or "General"
            problem_count = int(cluster.get("problem_count") or 1)

            pain_score = self._pain_score(text)
            frequency_score = self._frequency_score(problem_count)
            solution_gap_score = self._solution_gap_score(text)
            market_score = self._market_score(niche, text)
            build_complexity_score = self._build_complexity_score(text)
            opportunity_score = self._final_score(
                pain_score=pain_score,
                frequency_score=frequency_score,
                solution_gap_score=solution_gap_score,
                market_score=market_score,
                build_complexity_score=build_complexity_score,
            )

            row = Opportunity(
                cluster_id=cluster["cluster_db_id"],
                title=cluster.get("title") or f"Opportunity for {niche}",
                description=cluster.get("summary") or text,
                pain_score=pain_score,
                frequency_score=frequency_score,
                solution_gap_score=solution_gap_score,
                market_score=market_score,
                build_complexity_score=build_complexity_score,
                opportunity_score=opportunity_score,
                created_at=now,
            )
            session.add(row)
            session.flush()

            enriched = {
                **cluster,
                "opportunity_id": row.id,
                "opportunity_title": row.title,
                "opportunity_description": row.description,
                "pain_score": pain_score,
                "frequency_score": frequency_score,
                "solution_gap_score": solution_gap_score,
                "market_score": market_score,
                "build_complexity_score": build_complexity_score,
                "opportunity_score": opportunity_score,
            }
            discovered.append(enriched)

        top_score = max((item["opportunity_score"] for item in discovered), default=0.0)
        return {
            "clusters": discovered,
            "metrics": {
                "clusters_analyzed": len(clusters),
                "opportunities_discovered": len(discovered),
                "top_opportunity_score": top_score,
            },
        }
