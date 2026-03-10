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
    <article className="idea-card">
      <div className="idea-card-header">
        <span className="tag">{idea.niche}</span>
        <IdeaScore
          score={idea.score}
          tooltip="Суммарный score идеи: учитываются спрос, конкуренция, сложность реализации и монетизация."
        />
      </div>
      <h3>{idea.title}</h3>
      <p>{idea.summary}</p>
      <div className="meta-row">
        <span
          className="soft-tag"
          title={`Источник идеи: ${sourceLabel}. Возможные источники: reddit, hackernews, rss, internal clustering.`}
        >
          Источник: {sourceLabel}
        </span>
        <span title="Оценка сложности реализации идеи.">{idea.difficulty}</span>
        <span title="Предполагаемая модель монетизации идеи.">{idea.monetization}</span>
      </div>
      <div className="meta-row">
        <span className="idea-created-at">Создано: {createdAt}</span>
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
