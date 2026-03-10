import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchIdea } from "../api/ideas_api";

export default function IdeaDetail() {
  const { ideaId } = useParams();
  const [idea, setIdea] = useState(null);

  useEffect(() => {
    fetchIdea(ideaId).then(setIdea);
  }, [ideaId]);

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
        <h3>Целевая аудитория</h3>
        <p>{idea.audience}</p>
      </div>
      <div className="panel">
        <h3>Функции</h3>
        <ul>
          {idea.features.map((feature) => (
            <li key={feature}>{feature}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
