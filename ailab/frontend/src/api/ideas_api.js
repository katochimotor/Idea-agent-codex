const API_BASE = "/api";

export async function fetchIdeas() {
  const response = await fetch(`${API_BASE}/ideas`);
  return response.json();
}

export async function discoverIdeas() {
  const response = await fetch(`${API_BASE}/ideas/discover`, { method: "POST" });
  return response.json();
}

export async function fetchIdea(ideaId) {
  const response = await fetch(`${API_BASE}/ideas/${ideaId}`);
  return response.json();
}
