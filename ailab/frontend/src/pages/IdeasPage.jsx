import { useEffect, useState } from "react";
import { fetchIdeas } from "../api/ideas_api";
import IdeaList from "../components/IdeaList";

export default function IdeasPage() {
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchIdeas()
      .then((payload) => {
        setIdeas(payload);
        setErrorMessage("");
      })
      .catch((error) => {
        setErrorMessage(error.message || "Не удалось загрузить список идей.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <section>
      <div className="page-header">
        <h1>Все идеи</h1>
        <p>Список идей, найденных системой и сгенерированных ИИ.</p>
      </div>
      {loading ? <div className="panel"><p>Загрузка идей...</p></div> : null}
      {errorMessage ? <div className="panel"><p className="job-error">{errorMessage}</p></div> : null}
      {!loading && !errorMessage ? <IdeaList ideas={ideas} /> : null}
    </section>
  );
}
