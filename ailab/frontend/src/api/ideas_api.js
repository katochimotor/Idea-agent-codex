const API_BASE = "/api";

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

export async function fetchIdeas() {
  const response = await fetch(`${API_BASE}/ideas`);
  return parseJson(response);
}

export async function fetchIdea(ideaId) {
  const response = await fetch(`${API_BASE}/ideas/${ideaId}`);
  return parseJson(response);
}
