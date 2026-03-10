const API_BASE = "/api";

const DEFAULT_POLL_INTERVAL_MS = 1500;
const DEFAULT_TIMEOUT_MS = 45000;

export async function enqueueDiscoverJob() {
  const response = await fetch(`${API_BASE}/jobs/discover`, { method: "POST" });
  return response.json();
}

export async function fetchJob(jobId) {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`);
  return response.json();
}

function sleep(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

export async function waitForJob(jobId, options = {}) {
  const pollIntervalMs = options.pollIntervalMs ?? DEFAULT_POLL_INTERVAL_MS;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const startedAt = Date.now();

  while (Date.now() - startedAt < timeoutMs) {
    const job = await fetchJob(jobId);
    if (job.status === "completed") {
      return job;
    }
    if (job.status === "failed" || job.status === "cancelled") {
      throw new Error(job.error_message || `Job ${job.status}`);
    }
    await sleep(pollIntervalMs);
  }

  throw new Error("Job polling timed out");
}
