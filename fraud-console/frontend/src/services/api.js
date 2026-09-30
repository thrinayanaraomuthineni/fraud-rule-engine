async function req(path, opts = {}) {
  let res;
  try {
    res = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" }, ...opts });
  } catch {
    throw new Error("Cannot reach the API. Start the backend: uvicorn app.main:app --port 8000");
  }
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const { detail } = await res.json();
      msg = typeof detail === "string" ? detail
        : detail.map((d) => `${d.loc.slice(1).join(".")}: ${d.msg}`).join("; ");
    } catch { /* keep default message */ }
    throw new Error(msg);
  }
  return res.json();
}

const send = (method, body) => ({ method, body: JSON.stringify(body) });
const LISTS = { queue: "/transactions/flagged?status=PENDING", flagged: "/transactions/flagged", all: "/transactions" };

export const api = {
  list: (tab, q) => req(LISTS[tab] + (q ? (LISTS[tab].includes("?") ? "&" : "?") + `q=${encodeURIComponent(q)}` : "")),
  stats: () => req("/dashboard/stats"),
  get: (id) => req(`/transactions/${id}`),
  create: (body) => req("/transactions", send("POST", body)),
  evaluate: (id) => req(`/transactions/${id}/evaluate`, { method: "POST" }),
  review: (id, body) => req(`/transactions/${id}/review`, send("PATCH", body)),
};
