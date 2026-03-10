import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAnalytics, fetchDashboard } from "../api/dashboard_api";
import { fetchIdeas } from "../api/ideas_api";
import { enqueueDiscoverJob, fetchJob, fetchJobEvents } from "../api/jobs_api";
import { createProject } from "../api/projects_api";
import GenerateButton from "../components/GenerateButton";
import IdeaList from "../components/IdeaList";
import MindMapView from "../components/MindMapView";
import PipelineRunPanel from "../components/PipelineRunPanel";
import TrendGraph from "../components/TrendGraph";

export default function Dashboard() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState({
    trends: [],
    latest_results: [],
    top_opportunities: [],
    discovery_insights: [],
    latest_pipeline_run: null,
    latest_pipeline_events: []
  });
  const [analytics, setAnalytics] = useState({
    ideas_generated_today: 0,
    average_score: 0,
    top_niches: [],
    problems_detected: 0,
    clusters_detected: 0,
    top_opportunities: 0
  });
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [job, setJob] = useState(null);
  const [jobEvents, setJobEvents] = useState([]);
  const [pageError, setPageError] = useState("");
  const [pageLoading, setPageLoading] = useState(true);
  const [creatingProjectId, setCreatingProjectId] = useState(null);

  async function loadDashboardState() {
    const [dashboardPayload, analyticsPayload, ideasPayload] = await Promise.all([fetchDashboard(), fetchAnalytics(), fetchIdeas()]);
    setDashboard(dashboardPayload);
    setAnalytics(analyticsPayload);
    setIdeas(ideasPayload);
    setJob(dashboardPayload.latest_pipeline_run || null);
    setJobEvents(dashboardPayload.latest_pipeline_events || []);
  }

  useEffect(() => {
    loadDashboardState()
      .then(() => setPageError(""))
      .catch((error) => {
        setPageError(error.message || "Не удалось загрузить dashboard.");
      })
      .finally(() => {
        setPageLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!job?.id || ["completed", "failed", "cancelled"].includes(job.status) || !loading) {
      return undefined;
    }

    let active = true;
    const poll = async () => {
      try {
        const [nextJob, nextEvents] = await Promise.all([fetchJob(job.id), fetchJobEvents(job.id)]);
        if (!active) {
          return;
        }
        setJob(nextJob);
        setJobEvents(nextEvents);

        if (nextJob.status === "completed") {
          await loadDashboardState();
          if (!active) {
            return;
          }
          setLoading(false);
        } else if (nextJob.status === "failed" || nextJob.status === "cancelled") {
          setLoading(false);
        }
      } catch (error) {
        if (!active) {
          return;
        }
        setPageError(error.message || "Не удалось обновить состояние задачи.");
        setLoading(false);
      }
    };

    poll();
    const timer = window.setInterval(poll, 1500);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [job?.id, job?.status, loading]);

  async function handleDiscover() {
    setLoading(true);
    setPageError("");
    setJobEvents([]);
    try {
      const nextJob = await enqueueDiscoverJob();
      setJob({
        id: nextJob.job_id,
        status: nextJob.status,
        job_type: nextJob.job_type,
        result: null
      });
    } catch (error) {
      setLoading(false);
      setPageError(error.message || "Не удалось создать задачу поиска идей.");
    }
  }

  async function handleCreateProject(idea) {
    setCreatingProjectId(idea.id);
    setPageError("");
    try {
      await createProject({ idea_id: idea.id, title: idea.title });
      navigate("/projects");
    } catch (error) {
      setPageError(error.message || "Не удалось создать проект.");
    } finally {
      setCreatingProjectId(null);
    }
  }

  const latestIdeas = dashboard.latest_results?.length ? dashboard.latest_results : ideas.slice(0, 6);

  return (
    <div className="dashboard-layout">
      {pageError ? <div className="panel"><p className="job-error">{pageError}</p></div> : null}

      <section className="hero-panel">
        <div>
          <p className="eyebrow">Research Interface</p>
          <h1>{dashboard.hero_title || "AI Idea Research Lab"}</h1>
          <p>{dashboard.hero_subtitle}</p>
        </div>
        <GenerateButton onClick={handleDiscover} loading={loading} polling={Boolean(job?.id && loading)} />
      </section>

      <section className="stats-row">
        <div className="stat-card">
          <span>Ideas generated today</span>
          <strong>{analytics.ideas_generated_today ?? "-"}</strong>
        </div>
        <div className="stat-card">
          <span>Problems discovered</span>
          <strong>{analytics.problems_detected ?? "-"}</strong>
        </div>
        <div className="stat-card">
          <span>Clusters detected</span>
          <strong>{analytics.clusters_detected ?? "-"}</strong>
        </div>
        <div className="stat-card">
          <span>Top opportunities</span>
          <strong>{analytics.top_opportunities ?? "-"}</strong>
        </div>
      </section>

      <PipelineRunPanel job={job} events={jobEvents} loading={loading || pageLoading} />

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Latest Pipeline Results</h3>
            <p className="panel-subtitle">На dashboard остаются только результаты последнего pipeline run.</p>
          </div>
          <span className="soft-tag">{latestIdeas.length} ideas</span>
        </div>
        <IdeaList ideas={latestIdeas} onCreateProject={handleCreateProject} creatingProjectId={creatingProjectId} />
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Startup Opportunities</h3>
            <p className="panel-subtitle">Топ кластеров, отсортированных по opportunity score.</p>
          </div>
          <span className="tag">{dashboard.top_opportunities?.length || 0} clusters</span>
        </div>
        <div className="opportunity-grid">
          {dashboard.top_opportunities?.length ? (
            dashboard.top_opportunities.map((item) => (
              <button
                key={item.cluster_id}
                type="button"
                className="opportunity-card"
                onClick={() => navigate(`/opportunities/${item.cluster_id}`)}
              >
                <div className="panel-header">
                  <strong>{item.title}</strong>
                  <span className="tag">Score {item.opportunity_score}</span>
                </div>
                <p>{item.description}</p>
                <div className="opportunity-meta">
                  <span className="soft-tag">{item.problem_count} problems</span>
                  <span className="soft-tag">{item.related_ideas} related ideas</span>
                </div>
              </button>
            ))
          ) : (
            <p className="panel-subtitle">После первого pipeline run здесь появятся opportunity clusters.</p>
          )}
        </div>
      </section>

      <div className="dashboard-bottom">
        <section className="panel">
          <div className="panel-header">
            <h3>Idea Discovery Insights</h3>
          </div>
          <div className="trend-list">
            {dashboard.discovery_insights?.length ? (
              dashboard.discovery_insights.map((insight) => (
                <div key={insight.label} className="trend-pill">
                  {insight.label}: {insight.value}
                </div>
              ))
            ) : (
              <p className="panel-subtitle">Insights появятся после накопления новых запусков.</p>
            )}
          </div>
        </section>
        <TrendGraph trends={dashboard.trends} />
      </div>

      <MindMapView ideas={latestIdeas} />
    </div>
  );
}
