import { useEffect, useState } from "react";
import { api } from "../services/api";
import { RiskBadge, StatusBadge, money, txId, when } from "./ui";

const NOTICE = {
  SENT_AWS: "High-risk alert sent via AWS SNS.",
  SENT_MOCK: "High-risk alert logged by the local mock notifier (AWS not configured).",
  FAILED: "High-risk alert failed to send. Re-run the rules to retry.",
};

export default function DetailPanel({ id, onClose, onChanged }) {
  const [tx, setTx] = useState(null);
  const [note, setNote] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const apply = (t) => { setTx(t); setNote(t.reviewer_note || ""); };
  useEffect(() => {
    setTx(null); setErr("");
    api.get(id).then(apply).catch((e) => setErr(e.message));
  }, [id]);

  const run = async (call) => {
    setBusy(true); setErr("");
    try { apply(await call()); onChanged(); } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };
  const decide = (status) => run(() => api.review(id, { status, note }));

  return (
    <>
      <div className="scrim" onClick={onClose} />
      <aside className="drawer" role="dialog" aria-label="Transaction details">
        <div className="drawer-head">
          <h2>Transaction {txId(id)}</h2>
          <button className="icon" onClick={onClose} aria-label="Close">×</button>
        </div>
        {err && <div className="error">{err}</div>}
        {!tx ? (!err && <p className="pad muted">Loading…</p>) : (
          <div className="pad">
            <dl className="facts">
              <div><dt>Account</dt><dd>{tx.account_id}</dd></div>
              <div><dt>Amount</dt><dd>{money(tx.amount, tx.currency)}</dd></div>
              <div><dt>Location</dt><dd>{tx.location}</dd></div>
              <div><dt>Time</dt><dd>{when(tx.timestamp)}</dd></div>
              <div><dt>Risk</dt><dd><RiskBadge level={tx.risk_level} /></dd></div>
              <div><dt>Review status</dt><dd><StatusBadge status={tx.review_status} /></dd></div>
            </dl>

            <div className="meter" title={`${tx.risk_score} of 100`}>
              <div className={`fill risk-${tx.risk_level.toLowerCase()}`} style={{ width: `${tx.risk_score}%` }} />
              <span>Risk score {tx.risk_score} / 100</span>
            </div>

            <h3>Why this was flagged</h3>
            {tx.flags.length === 0 ? (
              <p className="muted">No fraud rules triggered for this transaction.</p>
            ) : (
              <ul className="rules">
                {tx.flags.map((f) => (
                  <li key={f.rule}>
                    <div><strong>{f.rule}</strong><span className="pts">+{f.risk}</span></div>
                    <p>{f.reason}</p>
                  </li>
                ))}
              </ul>
            )}
            <p className="muted small">A flag means the transaction needs investigation. It is not proof of fraud.</p>
            {tx.notification_status && <p className="small notice">{NOTICE[tx.notification_status]}</p>}

            <h3>Reviewer note</h3>
            <textarea rows="3" value={note} onChange={(e) => setNote(e.target.value)}
              placeholder="What did you check and what did you decide? Saved with your decision." />
            <div className="actions">
              <button className="btn primary" disabled={busy || tx.review_status === "REVIEWED"}
                onClick={() => decide("REVIEWED")}>Mark reviewed</button>
              <button className="btn" disabled={busy || tx.review_status === "CLEARED"}
                onClick={() => decide("CLEARED")}>Clear</button>
              {tx.review_status !== "PENDING" && (
                <button className="btn ghost" disabled={busy} onClick={() => decide("PENDING")}>Reopen</button>
              )}
              <button className="btn ghost right" disabled={busy}
                onClick={() => run(() => api.evaluate(id))}>Re-run rules</button>
            </div>
          </div>
        )}
      </aside>
    </>
  );
}
