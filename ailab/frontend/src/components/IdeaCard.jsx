import { Link } from "react-router-dom";
import IdeaScore from "./IdeaScore";

export default function IdeaCard({ idea, onCreateProject }) {
  return (
    <article className="idea-card">
      <div className="idea-card-header">
        <span className="tag">{idea.niche}</span>
        <IdeaScore score={idea.score} />
      </div>
      <h3>{idea.title}</h3>
      <p>{idea.summary}</p>
      <div className="meta-row">
        <span>{idea.source}</span>
        <span>{idea.difficulty}</span>
        <span>{idea.monetization}</span>
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
        <button className="text-button" type="button" onClick={() => onCreateProject?.(idea)}>
          Создать проект
        </button>
      </div>
    </article>
  );
}
