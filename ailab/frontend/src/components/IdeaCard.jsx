import { Link } from "react-router-dom";
import IdeaScore from "./IdeaScore";

function normalizeSourceLabel(source) {
  const normalized = (source || "").toLowerCase();
  if (normalized.includes("hacker")) {
    return "hackernews";
  }
  if (normalized.includes("reddit")) {
    return "reddit";
  }
  if (normalized.includes("rss")) {
    return "rss";
  }
  return normalized || "unknown";
}

export default function IdeaCard({ idea, onCreateProject }) {
  const sourceLabel = normalizeSourceLabel(idea.source);
  const createdAt = idea.created_at ? new Date(idea.created_at).toLocaleString() : "—";

  return (
    <article className="idea-card idea-card-rich">
      <div className="idea-card-header">
        <span className="tag">{idea.niche}</span>
        <IdeaScore
          score={idea.score}
          tooltip="Суммарный score идеи: учитываются спрос, конкуренция, сложность реализации и монетизация."
        />
      </div>

      <div className="idea-card-copy">
        <h3>{idea.title}</h3>
        <p className="panel-subtitle">{idea.problem}</p>
        <p>{idea.summary}</p>
      </div>

      <div className="idea-evidence">
        <div className="meta-row">
          <span
            className="soft-tag"
            title={`Источник идеи: ${sourceLabel}. Возможные источники: reddit, hackernews, rss, internal clustering.`}
          >
            Source: {sourceLabel}
          </span>
          {idea.opportunity_score ? <span className="soft-tag">Opportunity {idea.opportunity_score}</span> : null}
        </div>
        {idea.source_title ? <p><strong>Thread:</strong> {idea.source_title}</p> : null}
        {idea.audience ? <p><strong>Audience:</strong> {idea.audience}</p> : null}
        {idea.source_quote ? <blockquote className="idea-quote">“{idea.source_quote}”</blockquote> : null}
        {idea.source_url ? (
          <a className="text-link" href={idea.source_url} target="_blank" rel="noreferrer">
            Открыть источник
          </a>
        ) : null}
      </div>

      <div className="meta-row">
        <span className="idea-created-at">Создано: {createdAt}</span>
        <span title="Оценка сложности реализации идеи.">{idea.difficulty}</span>
        <span title="Предполагаемая модель монетизации идеи.">{idea.monetization}</span>
      </div>

      <div className="tag-row">
        {idea.tags?.map((tag) => (
          <span key={tag} className="soft-tag">
            {tag}
          </span>
        ))}
      </div>

      <div className="card-actions">
        <Link className="text-link" to={`/ideas/${idea.id}`}>
          Анализ
        </Link>
        {idea.cluster_id ? (
          <Link className="text-link" to={`/opportunities/${idea.cluster_id}`}>
            Cluster
          </Link>
        ) : null}
        {onCreateProject ? (
          <button
            className="text-button"
            type="button"
            onClick={() => onCreateProject(idea)}
            disabled={idea.creating_project}
          >
            {idea.creating_project ? "Создание..." : "Создать проект"}
          </button>
        ) : null}
      </div>
    </article>
  );
}
