import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchOpportunityDetail } from "../api/opportunities_api";

export default function OpportunityDetailPage() {
  const { clusterId } = useParams();
  const [payload, setPayload] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchOpportunityDetail(clusterId)
      .then((result) => {
        setPayload(result);
        setErrorMessage("");
      })
      .catch((error) => {
        setErrorMessage(error.message || "Не удалось загрузить opportunity cluster.");
      });
  }, [clusterId]);

  if (errorMessage) {
    return <section className="panel"><p className="job-error">{errorMessage}</p></section>;
  }

  if (!payload) {
    return <section className="panel"><p>Загрузка cluster details...</p></section>;
  }

  return (
    <section className="detail-layout">
      <div className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Opportunity Cluster</p>
            <h1>{payload.title}</h1>
          </div>
          <span className="tag">Score {payload.opportunity_score}</span>
        </div>
        <p>{payload.description}</p>
        <div className="pipeline-metrics-grid">
          <div className="metric-tile"><span>Pain</span><strong>{payload.pain_score}</strong></div>
          <div className="metric-tile"><span>Frequency</span><strong>{payload.frequency_score}</strong></div>
          <div className="metric-tile"><span>Solution Gap</span><strong>{payload.solution_gap_score}</strong></div>
          <div className="metric-tile"><span>Market</span><strong>{payload.market_score}</strong></div>
          <div className="metric-tile"><span>Build</span><strong>{payload.build_complexity_score}</strong></div>
          <div className="metric-tile"><span>Problems</span><strong>{payload.cluster.problem_count}</strong></div>
        </div>
      </div>

      <div className="panel">
        <h3>Cluster Summary</h3>
        <p>{payload.cluster.summary || payload.cluster_title}</p>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h3>Related Ideas</h3>
          <span className="soft-tag">{payload.related_ideas.length} ideas</span>
        </div>
        <div className="opportunity-grid">
          {payload.related_ideas.length ? (
            payload.related_ideas.map((idea) => (
              <article key={idea.id} className="opportunity-card">
                <strong>{idea.title}</strong>
                <p>{idea.summary}</p>
                <div className="card-actions">
                  <span className="soft-tag">{idea.opportunity_score ?? "—"}</span>
                  <Link className="text-link" to={`/ideas/${idea.id}`}>Открыть идею</Link>
                </div>
              </article>
            ))
          ) : (
            <p className="panel-subtitle">Для этого кластера идеи пока не привязаны.</p>
          )}
        </div>
      </div>
    </section>
  );
}
