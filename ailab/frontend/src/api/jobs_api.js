const API_BASE = "/api";

const DEFAULT_POLL_INTERVAL_MS = 1500;
const DEFAULT_TIMEOUT_MS = 45000;

async function parseJson(response) {
  const rawText = await response.text();
  let payload = {};
  try {
    payload = rawText ? JSON.parse(rawText) : {};
  } catch {
    payload = { detail: rawText || "Unexpected server response" };
  }
  if (!response.ok) {
    throw new Error(payload.detail || "Request failed");
  }
  return payload;
}

export async function enqueueDiscoverJob() {
  const response = await fetch(`${API_BASE}/jobs/discover`, { method: "POST" });
  return parseJson(response);
}

export async function fetchJob(jobId) {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`);
  return parseJson(response);
}

export async function fetchJobEvents(jobId) {
  const response = await fetch(`${API_BASE}/jobs/${jobId}/events`);
  return parseJson(response);
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
    if (options.onProgress) {
      const events = await fetchJobEvents(jobId);
      options.onProgress({ job, events });
    }
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
