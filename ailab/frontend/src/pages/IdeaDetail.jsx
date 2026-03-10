import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchIdea } from "../api/ideas_api";

const SCORE_TOOLTIPS = {
  market_demand: "Насколько заметен и повторяем спрос на решение этой проблемы.",
  competition: "Насколько плотная конкуренция в этой нише. Более высокий балл означает более благоприятную ситуацию в текущей модели.",
  difficulty: "Сложность реализации MVP с текущим стеком и типичной командой.",
  monetization: "Насколько понятен и реалистичен путь к монетизации идеи.",
  total: "Суммарный score идеи на основе ключевых продуктовых метрик."
};

export default function IdeaDetail() {
  const { ideaId } = useParams();
  const [idea, setIdea] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchIdea(ideaId)
      .then((payload) => {
        setIdea(payload);
        setErrorMessage("");
      })
      .catch((error) => {
        setErrorMessage(error.message || "Не удалось загрузить детали идеи.");
      });
  }, [ideaId]);

  if (errorMessage) {
    return (
      <section className="detail-layout">
        <div className="panel">
          <p className="job-error">{errorMessage}</p>
        </div>
      </section>
    );
  }

  if (!idea) {
    return <div className="panel">Загрузка...</div>;
  }

  return (
    <section className="detail-layout">
      <div className="panel">
        <h1>{idea.title}</h1>
        <p>{idea.summary}</p>
      </div>
      <div className="panel">
        <h3>Проблема</h3>
        <p>{idea.problem}</p>
      </div>
      <div className="panel">
        <div className="panel-header">
          <h3>Source Traceability</h3>
          {idea.source ? <span className="soft-tag">{idea.source}</span> : null}
        </div>
        {idea.source_title ? <p><strong>Thread:</strong> {idea.source_title}</p> : null}
        {idea.source_quote ? <blockquote className="idea-quote">“{idea.source_quote}”</blockquote> : null}
        <div className="card-actions">
          {idea.source_url ? (
            <a className="text-link" href={idea.source_url} target="_blank" rel="noreferrer">
              Открыть обсуждение
            </a>
          ) : null}
          {idea.cluster_id ? (
            <Link className="text-link" to={`/opportunities/${idea.cluster_id}`}>
              Cluster details
            </Link>
          ) : null}
        </div>
      </div>
      <div className="panel">
        <h3>Целевая аудитория</h3>
        <p>{idea.audience}</p>
      </div>
      <div className="panel">
        <h3>Оценка</h3>
        <div className="score-grid">
          <div className="score-metric" title={SCORE_TOOLTIPS.market_demand}>
            <span>Спрос</span>
            <strong>{idea.score.market_demand}</strong>
          </div>
          <div className="score-metric" title={SCORE_TOOLTIPS.competition}>
            <span>Конкуренция</span>
            <strong>{idea.score.competition}</strong>
          </div>
          <div className="score-metric" title={SCORE_TOOLTIPS.difficulty}>
            <span>Сложность</span>
            <strong>{idea.score.difficulty}</strong>
          </div>
          <div className="score-metric" title={SCORE_TOOLTIPS.monetization}>
            <span>Монетизация</span>
            <strong>{idea.score.monetization}</strong>
          </div>
          <div className="score-metric score-metric-total" title={SCORE_TOOLTIPS.total}>
            <span>Итоговый score</span>
            <strong>{idea.score.total}</strong>
          </div>
        </div>
      </div>
      <div className="panel">
        <h3>Функции</h3>
        <ul>
          {idea.features.map((feature) => (
            <li key={feature}>{feature}</li>
          ))}
        </ul>
      </div>
      <div className="panel">
        <div className="panel-header">
          <h3>Отчёт</h3>
          <div className="meta-row">
            {idea.opportunity_score ? <span className="soft-tag">Opportunity {idea.opportunity_score}</span> : null}
            <span className="soft-tag" title={idea.report_path || "Путь к markdown-отчёту"}>
              Markdown
            </span>
          </div>
        </div>
        <p className="panel-subtitle">{idea.report_path || "Путь к отчёту пока не задан."}</p>
        <pre className="report-preview">{idea.report_content || "Отчёт ещё не сгенерирован."}</pre>
      </div>
    </section>
  );
}
