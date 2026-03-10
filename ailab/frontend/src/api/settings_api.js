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

export async function fetchProviderSettings() {
  const response = await fetch(`${API_BASE}/settings/providers`);
  return parseJson(response);
}

export async function testProviderConnection(payload) {
  const response = await fetch(`${API_BASE}/settings/providers/test`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
  return parseJson(response);
}

export async function saveProviderSettings(payload) {
  const response = await fetch(`${API_BASE}/settings/providers/save`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
  return parseJson(response);
}
