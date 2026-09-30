import { useState } from "react";
import { api } from "../services/api";

const PLACES = {
  Hyderabad: [17.385, 78.4867], Mumbai: [19.076, 72.8777], Bengaluru: [12.9716, 77.5946],
  Delhi: [28.6139, 77.209], London: [51.5074, -0.1278], Singapore: [1.3521, 103.8198],
  "New York": [40.7128, -74.006],
};

export default function NewTransaction({ onClose, onCreated }) {
  const [f, setF] = useState({ account_id: "ACC-101", amount: "", currency: "INR", location: "Hyderabad", when: "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setErr("");
    const [latitude, longitude] = PLACES[f.location];
    try {
      const tx = await api.create({
        account_id: f.account_id.trim(), amount: Number(f.amount), currency: f.currency,
        location: f.location, latitude, longitude,
        timestamp: f.when ? new Date(f.when).toISOString() : null,
      });
      onCreated(tx);
    } catch (e2) { setErr(e2.message); } finally { setBusy(false); }
  };

  return (
    <>
      <div className="scrim" onClick={onClose} />
      <form className="modal" onSubmit={submit}>
        <h2>New transaction</h2>
        <p className="muted small">It is scored against the account's existing history. Leave the time empty to use now.</p>
        {err && <div className="error">{err}</div>}
        <label>Account<input required value={f.account_id} onChange={set("account_id")} /></label>
        <div className="row2">
          <label>Amount<input required type="number" min="1" step="any" value={f.amount} onChange={set("amount")} /></label>
          <label>Currency<input required maxLength="3" value={f.currency} onChange={set("currency")} /></label>
        </div>
        <label>Location
          <select value={f.location} onChange={set("location")}>
            {Object.keys(PLACES).map((p) => <option key={p}>{p}</option>)}
          </select>
        </label>
        <label>Time (optional)<input type="datetime-local" value={f.when} onChange={set("when")} /></label>
        <div className="actions">
          <button className="btn primary" disabled={busy}>{busy ? "Scoring…" : "Add and score"}</button>
          <button type="button" className="btn ghost" onClick={onClose}>Cancel</button>
        </div>
      </form>
    </>
  );
}
