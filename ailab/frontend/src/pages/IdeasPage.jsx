import { useEffect, useState } from "react";
import { fetchIdeas } from "../api/ideas_api";
import IdeaList from "../components/IdeaList";

export default function IdeasPage() {
  const [ideas, setIdeas] = useState([]);

  useEffect(() => {
    fetchIdeas().then(setIdeas);
  }, []);

  return (
    <section>
      <div className="page-header">
        <h1>Все идеи</h1>
        <p>Список идей, найденных системой и сгенерированных ИИ.</p>
      </div>
      <IdeaList ideas={ideas} />
    </section>
  );
}
