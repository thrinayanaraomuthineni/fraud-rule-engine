export const txId = (id) => `TX-${String(id).padStart(4, "0")}`;

export const money = (n, cur = "INR") => {
  try {
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: cur, maximumFractionDigits: 0 }).format(n);
  } catch {
    return `${cur} ${n}`;
  }
};

// The API returns naive UTC timestamps.
export const when = (ts) =>
  new Date(/Z|[+-]\d\d:\d\d$/.test(ts) ? ts : ts + "Z").toLocaleString("en-GB", {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
  });

export const RiskBadge = ({ level }) => (
  <span className={`badge risk-${level.toLowerCase()}`}>{level[0] + level.slice(1).toLowerCase()}</span>
);

const STATUS = { PENDING: "Pending", REVIEWED: "Reviewed", CLEARED: "Cleared" };
export const StatusBadge = ({ status }) => (
  <span className={`status st-${status.toLowerCase()}`}>{STATUS[status]}</span>
);
