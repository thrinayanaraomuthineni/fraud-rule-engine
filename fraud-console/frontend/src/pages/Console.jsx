import { useCallback, useEffect, useState } from "react";
import { api } from "../services/api";
import DetailPanel from "../components/DetailPanel";
import NewTransaction from "../components/NewTransaction";
import { RiskBadge, StatusBadge, money, txId, when } from "../components/ui";

const TABS = [["queue", "Needs review"], ["flagged", "All flagged"], ["all", "All transactions"]];

export default function Console({ showNew, onCloseNew }) {
  const [tab, setTab] = useState("queue");
  const [q, setQ] = useState("");
  const [rows, setRows] = useState(null);
  const [stats, setStats] = useState(null);
  const [openId, setOpenId] = useState(null);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const [list, s] = await Promise.all([api.list(tab, q.trim()), api.stats()]);
      // Review queues: highest risk first. Full list: newest first (API order).
      setRows(tab === "all" ? list : [...list].sort((a, b) => b.risk_score - a.risk_score));
      setStats(s);
      setError("");
    } catch (e) { setError(e.message); }
  }, [tab, q]);

  useEffect(() => { const t = setTimeout(load, 200); return () => clearTimeout(t); }, [load]);

  const counts = stats && { queue: stats.pending_reviews, flagged: stats.flagged, all: stats.total };
  const tiles = stats && [
    ["Total transactions", stats.total], ["Flagged", stats.flagged],
    ["High risk", stats.high_risk, "danger"], ["Pending review", stats.pending_reviews, "alert"],
  ];

  return (
    <main>
      {error && <div className="error">{error} <button className="link" onClick={load}>Retry</button></div>}

      <section className="stats">
        {(tiles || [1, 2, 3, 4].map(() => ["…", "–"])).map(([label, n, cls], i) => (
          <div key={i} className={`tile ${cls || ""}`}><b>{n}</b><span>{label}</span></div>
        ))}
      </section>
      {stats && (
        <p className="meta">
          Rule hits: {Object.keys(stats.by_rule).length
            ? Object.entries(stats.by_rule).map(([r, n]) => `${r} ${n}`).join(", ") : "none yet"}.
          {" "}Alerts fire at score {stats.high_threshold} or more via {stats.notifier === "AWS"
            ? "AWS SNS." : "the local mock notifier (AWS credentials not set)."}
        </p>
      )}

      <div className="toolbar">
        <nav className="tabs">
          {TABS.map(([key, label]) => (
            <button key={key} className={tab === key ? "on" : ""} onClick={() => setTab(key)}>
              {label}{counts && <em>{counts[key]}</em>}
            </button>
          ))}
        </nav>
        <input type="search" placeholder="Search account, location or TX id" value={q}
          onChange={(e) => setQ(e.target.value)} aria-label="Search transactions" />
      </div>

      <div className="tablewrap">
        <table>
          <thead>
            <tr>
              <th>Transaction</th><th>Account</th><th className="num">Amount</th><th>Location</th>
              <th>Risk</th><th className="num">Score</th><th>Triggered rules</th><th>Status</th><th>Time</th>
            </tr>
          </thead>
          <tbody>
            {(rows || []).map((t) => (
              <tr key={t.id} className={`lvl-${t.risk_level.toLowerCase()} ${t.id === openId ? "sel" : ""}`}
                onClick={() => setOpenId(t.id)}>
                <td className="mono">{txId(t.id)}</td>
                <td>{t.account_id}</td>
                <td className="num">{money(t.amount, t.currency)}</td>
                <td>{t.location}</td>
                <td><RiskBadge level={t.risk_level} /></td>
                <td className="num">{t.risk_score}</td>
                <td>{t.flags.length ? t.flags.map((f) => <span key={f.rule} className="chip">{f.rule}</span>) : <span className="muted">None</span>}</td>
                <td><StatusBadge status={t.review_status} /></td>
                <td className="nowrap">{when(t.timestamp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows && rows.length === 0 && (
          <p className="empty">
            {q ? "No transactions match your search."
              : stats?.total === 0 ? "No transactions yet. Run `python -m app.seed` in backend/, or add one with New transaction."
              : tab === "queue" ? "Nothing needs review right now." : "No transactions in this view."}
          </p>
        )}
        {!rows && !error && <p className="empty">Loading…</p>}
      </div>

      {openId && <DetailPanel id={openId} onClose={() => setOpenId(null)} onChanged={load} />}
      {showNew && (
        <NewTransaction onClose={onCloseNew}
          onCreated={(tx) => { onCloseNew(); setOpenId(tx.id); load(); }} />
      )}
    </main>
  );
}
