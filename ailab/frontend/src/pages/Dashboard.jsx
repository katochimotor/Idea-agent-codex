import { useEffect, useState } from "react";
import { fetchAnalytics, fetchDashboard } from "../api/dashboard_api";
import { fetchIdeas } from "../api/ideas_api";
import { enqueueDiscoverJob, waitForJob } from "../api/jobs_api";
import { createProject } from "../api/projects_api";
import GenerateButton from "../components/GenerateButton";
import IdeaList from "../components/IdeaList";
import MindMapView from "../components/MindMapView";
import TrendGraph from "../components/TrendGraph";

export default function Dashboard() {
  const [dashboard, setDashboard] = useState({ trends: [] });
  const [analytics, setAnalytics] = useState({});
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDashboard().then(setDashboard);
    fetchAnalytics().then(setAnalytics);
    fetchIdeas().then(setIdeas);
  }, []);

  async function handleDiscover() {
    setLoading(true);
    try {
      const job = await enqueueDiscoverJob();
      await waitForJob(job.job_id);
      const nextIdeas = await fetchIdeas();
      setIdeas(nextIdeas);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateProject(idea) {
    await createProject({ idea_id: idea.id, title: idea.title });
  }

  return (
    <div className="dashboard-layout">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Исследование рынка</p>
          <h1>{dashboard.hero_title || "Лаборатория идей"}</h1>
          <p>{dashboard.hero_subtitle}</p>
        </div>
        <GenerateButton onClick={handleDiscover} loading={loading} />
      </section>

      <section className="stats-row">
        <div className="stat-card">
          <span>Идей сегодня</span>
          <strong>{analytics.ideas_generated_today ?? "-"}</strong>
        </div>
        <div className="stat-card">
          <span>Средний score</span>
          <strong>{analytics.average_score ?? "-"}</strong>
        </div>
        <div className="stat-card">
          <span>Главные ниши</span>
          <strong>{analytics.top_niches?.join(", ") || "-"}</strong>
        </div>
      </section>

      <IdeaList ideas={ideas} onCreateProject={handleCreateProject} />

      <div className="dashboard-bottom">
        <TrendGraph trends={dashboard.trends} />
        <MindMapView />
      </div>
    </div>
  );
}
