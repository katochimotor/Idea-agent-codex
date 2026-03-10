import { useEffect, useState } from "react";
import { fetchProjects } from "../api/projects_api";

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchProjects()
      .then((payload) => {
        setProjects(payload);
        setErrorMessage("");
      })
      .catch((error) => {
        setErrorMessage(error.message || "Не удалось загрузить проекты.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <section className="panel">
      <h1>Проекты</h1>
      {loading ? <p>Загрузка проектов...</p> : null}
      {errorMessage ? <p className="job-error">{errorMessage}</p> : null}
      {!loading && !errorMessage && !projects.length ? <p>Проекты пока не созданы.</p> : null}
      <div className="settings-provider-list">
        {projects.map((project) => (
          <div key={project.id} className="settings-provider-card">
            <div className="panel-header">
              <strong>{project.title}</strong>
              <span className="soft-tag">{project.status}</span>
            </div>
            <p>Idea ID: {project.idea_id}</p>
            <p>Папка: {project.folder_path}</p>
            <p>Создано: {new Date(project.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
