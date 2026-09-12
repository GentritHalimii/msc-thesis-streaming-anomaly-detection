// Thin fetch layer. Every call returns parsed JSON or throws with the
// server's Albanian detail message, which the UI shows verbatim.

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = `${response.status}`;
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return response.json();
}

export const api = {
  meta: () => request("/api/meta"),
  page: (id) => request(`/api/page/${id}`),
  table: (name, query) =>
    request(`/api/table/${name}${query ? `?query=${encodeURIComponent(query)}` : ""}`),
  catalog: () => request("/api/catalog"),
  jobs: () => request("/api/jobs"),
  job: (id) => request(`/api/jobs/${id}`),
  run: (target) => request("/api/jobs", { method: "POST", body: JSON.stringify({ target }) }),
  cancel: (id) => request(`/api/jobs/${id}/cancel`, { method: "POST" }),
  services: () => request("/api/services"),
  compose: (action) =>
    request("/api/services/compose", { method: "POST", body: JSON.stringify({ action }) }),
  database: () => request("/api/database"),
  provenance: () => request("/api/provenance"),
};

/** Tail a job's log over server-sent events. Returns a close() function. */
export function followJob(jobId, { onLog, onState, onEnd, from = 0 }) {
  const source = new EventSource(`/api/jobs/${jobId}/stream?from=${from}`);
  source.addEventListener("hello", (event) => onState?.(JSON.parse(event.data).job));
  source.addEventListener("log", (event) => onLog?.(JSON.parse(event.data).lines));
  source.addEventListener("tick", (event) => onState?.(JSON.parse(event.data).job));
  source.addEventListener("end", (event) => {
    const payload = JSON.parse(event.data);
    onState?.(payload.job);
    onEnd?.(payload.job);
    source.close();
  });
  source.onerror = () => source.close();
  return () => source.close();
}
