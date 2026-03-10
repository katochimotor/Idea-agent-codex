const API_BASE = "/api";

export async function fetchDashboard() {
  const response = await fetch(`${API_BASE}/dashboard`);
  return response.json();
}

export async function fetchAnalytics() {
  const response = await fetch(`${API_BASE}/dashboard/analytics`);
  return response.json();
}
