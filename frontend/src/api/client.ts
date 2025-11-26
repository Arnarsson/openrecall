const API_BASE = '/api';

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getEntries(params: {
  page?: number;
  limit?: number;
  start_date?: number;
  end_date?: number;
  app?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set('page', params.page.toString());
  if (params.limit) searchParams.set('limit', params.limit.toString());
  if (params.start_date) searchParams.set('start_date', params.start_date.toString());
  if (params.end_date) searchParams.set('end_date', params.end_date.toString());
  if (params.app) searchParams.set('app', params.app);

  const query = searchParams.toString();
  return fetchJson(`${API_BASE}/entries${query ? `?${query}` : ''}`);
}

export async function getEntry(id: number) {
  return fetchJson(`${API_BASE}/entries/${id}`);
}

export async function searchEntries(query: string, limit: number = 20) {
  return fetchJson(`${API_BASE}/search?q=${encodeURIComponent(query)}&limit=${limit}`);
}

export async function getTimeline() {
  return fetchJson(`${API_BASE}/timeline`);
}

export async function getStats() {
  return fetchJson(`${API_BASE}/stats`);
}

export async function getApps() {
  return fetchJson(`${API_BASE}/apps`);
}

export async function getStatus() {
  return fetchJson(`${API_BASE}/status`);
}
