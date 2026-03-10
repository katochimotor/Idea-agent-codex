import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAnalytics, fetchDashboard } from "../api/dashboard_api";
import { fetchIdeas } from "../api/ideas_api";
import { enqueueDiscoverJob, fetchJob, fetchJobEvents } from "../api/jobs_api";
import { createProject } from "../api/projects_api";
import GenerateButton from "../components/GenerateButton";
import IdeaList from "../components/IdeaList";
import MindMapView from "../components/MindMapView";
import TrendGraph from "../components/TrendGraph";

const JOB_STATUS_LABELS = {
  queued: "В очереди",
  running: "Выполняется",
  completed: "Завершено",
  failed: "Ошибка",
  cancelled: "Отменено",
  retrying: "Повтор"
};

function buildJobProgress(job, events) {
  if (!job) {
    return 0;
  }
  if (job.status === "completed" || job.status === "failed" || job.status === "cancelled") {
    return 100;
  }
  if (job.status === "running") {
    return Math.min(30 + (events.length * 15), 90);
  }
  if (job.status === "queued" || job.status === "retrying") {
    return 15;
  }
  return 0;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState({ trends: [] });
  const [analytics, setAnalytics] = useState({
    ideas_generated_today: 0,
    average_score: 0,
    top_niches: [],
    problems_detected: 0
  });
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [job, setJob] = useState(null);
  const [jobEvents, setJobEvents] = useState([]);
  const [jobError, setJobError] = useState("");
  const [pageError, setPageError] = useState("");
  const [pageLoading, setPageLoading] = useState(true);
  const [creatingProjectId, setCreatingProjectId] = useState(null);

  useEffect(() => {
    Promise.all([fetchDashboard(), fetchAnalytics(), fetchIdeas()])
      .then(([dashboardPayload, analyticsPayload, ideasPayload]) => {
        setDashboard(dashboardPayload);
        setAnalytics(analyticsPayload);
        setIdeas(ideasPayload);
        setPageError("");
      })
      .catch((error) => {
        setPageError(error.message || "Не удалось загрузить dashboard.");
      })
      .finally(() => {
        setPageLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!job?.id || ["completed", "failed", "cancelled"].includes(job.status)) {
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
          const [nextIdeas, nextAnalytics] = await Promise.all([fetchIdeas(), fetchAnalytics()]);
          if (!active) {
            return;
          }
          setIdeas(nextIdeas);
          setAnalytics(nextAnalytics);
          setLoading(false);
          setJobError("");
        } else if (nextJob.status === "failed" || nextJob.status === "cancelled") {
          setLoading(false);
          setJobError(nextJob.error_message || `Задача завершилась со статусом ${nextJob.status}`);
        }
      } catch (error) {
        if (!active) {
          return;
        }
        setLoading(false);
        setJobError(error.message || "Не удалось обновить состояние задачи.");
      }
    };

    poll();
    const timer = window.setInterval(poll, 1500);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [job?.id, job?.status]);

  async function handleDiscover() {
    setLoading(true);
    setJobError("");
    setJobEvents([]);
    try {
      const nextJob = await enqueueDiscoverJob();
      setJob({
        id: nextJob.job_id,
        status: nextJob.status,
        job_type: nextJob.job_type
      });
    } catch (error) {
      setLoading(false);
      setJobError(error.message || "Не удалось создать задачу поиска идей.");
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

  const progressValue = buildJobProgress(job, jobEvents);
  const latestEvent = jobEvents[jobEvents.length - 1];
  const currentStage = latestEvent?.payload?.stage_label || "Ожидание";
  const jobPanelMessage =
    jobError || latestEvent?.message || (loading ? "Ожидаем новые события pipeline..." : "Pipeline ещё не запускался.");

  return (
    <div className="dashboard-layout">
      {pageError ? <div className="panel"><p className="job-error">{pageError}</p></div> : null}
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Исследование рынка</p>
          <h1>{dashboard.hero_title || "Лаборатория идей"}</h1>
          <p>{dashboard.hero_subtitle}</p>
        </div>
        <GenerateButton onClick={handleDiscover} loading={loading} polling={Boolean(job?.id && loading)} />
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
          <span>Проблем найдено</span>
          <strong>{analytics.problems_detected ?? "-"}</strong>
        </div>
        <div className="stat-card">
          <span>Главные ниши</span>
          <strong>{analytics.top_niches?.join(", ") || "-"}</strong>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Прогресс pipeline</h3>
            <p className="panel-subtitle">
              {job
                ? `Задача #${job.id}: ${JOB_STATUS_LABELS[job.status] || job.status}`
                : "Активных задач пока нет"}
            </p>
          </div>
          {job && <span className="tag">Job #{job.id}</span>}
        </div>
        <p className="panel-subtitle">Стадия: {currentStage}</p>

        <div className="job-progress-bar" aria-hidden="true">
          <div className="job-progress-fill" style={{ width: `${progressValue}%` }} />
        </div>

        <p className={jobError ? "job-error" : "panel-subtitle"}>{jobPanelMessage}</p>

        <div className="job-events">
          {jobEvents.length ? (
            jobEvents.map((event) => (
              <div key={event.id} className="job-event-row">
                <span className="soft-tag">{event.payload?.stage_label || JOB_STATUS_LABELS[event.status] || event.event_type}</span>
                <span>{event.message}</span>
                <span className="job-event-time">{new Date(event.created_at).toLocaleTimeString()}</span>
              </div>
            ))
          ) : (
            <p className="panel-subtitle">
              {pageLoading ? "Загружаем состояние dashboard..." : "После запуска поиска здесь появятся реальные события job worker."}
            </p>
          )}
        </div>
      </section>

      <IdeaList ideas={ideas} onCreateProject={handleCreateProject} creatingProjectId={creatingProjectId} />

      <div className="dashboard-bottom">
        <TrendGraph trends={dashboard.trends} />
        <MindMapView ideas={ideas} />
      </div>
    </div>
  );
}
