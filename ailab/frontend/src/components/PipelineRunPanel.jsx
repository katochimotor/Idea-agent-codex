const STAGES = [
  { key: "collect_documents", label: "Collecting documents" },
  { key: "extract_problems", label: "Extracting problems" },
  { key: "cluster_problems", label: "Clustering problems" },
  { key: "opportunity_analysis", label: "Opportunity analysis" },
  { key: "generate_ideas", label: "Generating ideas" },
  { key: "score_ideas", label: "Scoring ideas" },
  { key: "save_results", label: "Saving results" }
];

const STATUS_LABELS = {
  queued: "В очереди",
  running: "Выполняется",
  completed: "Завершено",
  failed: "Ошибка",
  cancelled: "Отменено",
  retrying: "Повтор"
};

function buildMetrics(job, events) {
  const merged = { ...(job?.pipeline_metrics || {}), ...(job?.result?.pipeline_metrics || {}) };
  for (const event of events) {
    if (!event.payload) {
      continue;
    }
    for (const [key, value] of Object.entries(event.payload)) {
      if (typeof value === "number") {
        merged[key] = value;
      }
    }
  }
  return merged;
}

function currentStage(events) {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const stage = events[index]?.payload?.stage;
    if (stage) {
      return stage;
    }
  }
  return null;
}

export default function PipelineRunPanel({ job, events = [], loading = false }) {
  const stageKey = currentStage(events) || (job?.status === "completed" ? "save_results" : null);
  const stageIndex = STAGES.findIndex((item) => item.key === stageKey);
  const stepNumber = stageIndex >= 0 ? stageIndex + 1 : 0;
  const progress = job?.status === "completed" ? 100 : stageIndex >= 0 ? Math.round(((stageIndex + 1) / STAGES.length) * 100) : 8;
  const stageLabel = STAGES.find((item) => item.key === stageKey)?.label || "Waiting";
  const metrics = buildMetrics(job, events);
  const panelMessage =
    job?.error_message
    || events[events.length - 1]?.message
    || (loading ? "Pipeline работает..." : "Pipeline ещё не запускался.");

  return (
    <section className="panel pipeline-panel">
      <div className="panel-header">
        <div>
          <h3>Latest Pipeline Run</h3>
          <p className="panel-subtitle">
            {job ? `Job #${job.id} · ${STATUS_LABELS[job.status] || job.status}` : "Активных запусков пока нет"}
          </p>
        </div>
        {job ? <span className="tag">Step {stepNumber || "0"} / {STAGES.length}</span> : null}
      </div>

      <div className="pipeline-stage-row">
        <div>
          <strong>{loading || job ? "Finding ideas..." : "Research pipeline idle"}</strong>
          <p className="panel-subtitle">{stageLabel}</p>
        </div>
        <span className="soft-tag">{progress}%</span>
      </div>

      <div className="job-progress-bar" aria-hidden="true">
        <div className="job-progress-fill" style={{ width: `${progress}%` }} />
      </div>

      <p className={job?.status === "failed" ? "job-error" : "panel-subtitle"}>{panelMessage}</p>

      <div className="pipeline-metrics-grid">
        <div className="metric-tile"><span>Documents scanned</span><strong>{metrics.documents_scanned ?? 0}</strong></div>
        <div className="metric-tile"><span>Problems extracted</span><strong>{metrics.problems_extracted ?? 0}</strong></div>
        <div className="metric-tile"><span>Clusters detected</span><strong>{metrics.clusters_detected ?? 0}</strong></div>
        <div className="metric-tile"><span>Opportunities</span><strong>{metrics.opportunities_discovered ?? 0}</strong></div>
        <div className="metric-tile"><span>Ideas generated</span><strong>{metrics.ideas_generated ?? 0}</strong></div>
        <div className="metric-tile"><span>New ideas added</span><strong>{metrics.new_ideas_added ?? 0}</strong></div>
        <div className="metric-tile"><span>Duplicates skipped</span><strong>{metrics.duplicates_skipped ?? 0}</strong></div>
        <div className="metric-tile"><span>Top opportunity</span><strong>{metrics.top_opportunity_score ?? 0}</strong></div>
      </div>

      <details className="pipeline-log-panel">
        <summary>Advanced logs</summary>
        <div className="job-events">
          {events.length ? (
            events.map((event) => (
              <div key={event.id} className="job-event-row">
                <span className="soft-tag">{event.payload?.stage_label || event.event_type}</span>
                <span>{event.message}</span>
                <span className="job-event-time">{new Date(event.created_at).toLocaleTimeString()}</span>
              </div>
            ))
          ) : (
            <p className="panel-subtitle">Логи появятся после первого запуска pipeline.</p>
          )}
        </div>
      </details>
    </section>
  );
}
