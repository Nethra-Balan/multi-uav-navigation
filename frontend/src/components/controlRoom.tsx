import type { ReactNode } from "react";
import type { FinalResult, Lifecycle } from "../types";

export const fmt = (value: number | undefined, digits = 2) => value === undefined ? "—" : value.toFixed(digits);

export function Status({ value }: { value: string }) {
  return <span className={`status status-${value}`}>{value.replace("_", " ")}</span>;
}

export function Metric({ label, value, unit, tone = "cyan" }: { label: string; value: string; unit?: string; tone?: "cyan" | "green" | "amber" | "red" }) {
  return <div className={`metric metric-${tone}`}><span>{label}</span><strong>{value}</strong>{unit && <small>{unit}</small>}</div>;
}

export function Panel({ title, eyebrow, children, className = "" }: { title: string; eyebrow?: string; children: ReactNode; className?: string }) {
  return <section className={`panel ${className}`}><div className="panel-head"><div>{eyebrow && <span className="eyebrow">{eyebrow}</span>}<h3>{title}</h3></div></div>{children}</section>;
}

export function Empty({ title, text, action, actionLabel = "Configure mission" }: { title: string; text: string; action?: () => void; actionLabel?: string }) {
  return <div className="empty"><div className="empty-mark"><span>+</span></div><span className="empty-kicker">SYSTEM STANDBY</span><h3>{title}</h3><p>{text}</p>{action && <button className="button primary" onClick={action}>{actionLabel}</button>}</div>;
}

export function FleetList({ rows, lifecycle, onSelect }: { rows: { uav: number; targetCount: number; distance?: number; targets?: number[] }[]; lifecycle: Lifecycle; onSelect?: (uav: number) => void }) {
  return <div className="fleet-list">{rows.map((row) => <button className="fleet-row fleet-row-button" key={row.uav} onClick={() => onSelect?.(row.uav)}>
    <span className="uav-id">UAV-{String(row.uav).padStart(2, "0")}</span>
    <span className={`fleet-state fleet-state-${lifecycle}`}><i />{lifecycle === "completed" ? "COMPLETE" : lifecycle.toUpperCase()}</span>
    <b>{row.targetCount.toString().padStart(2, "0")} targets</b>
    <span>{fmt(row.distance)} m</span>
    {row.targets && <small>{row.targets.join(" · ")}</small>}
  </button>)}</div>;
}

export function History({ data, color, label }: { data: (number | undefined)[]; color: string; label: string }) {
  const valid = data.filter((x): x is number => x !== undefined);
  if (!valid.length) return <div className="chart-empty">WAITING FOR GENERATION DATA</div>;
  const max = Math.max(...valid); const min = Math.min(...valid);
  const points = valid.map((v, i) => `${i / Math.max(valid.length - 1, 1) * 100},${100 - ((v - min) / Math.max(max - min, 1) * 78 + 10)}`).join(" ");
  return <div className="chart"><div className="chart-head"><span>{label}</span><b>{fmt(valid[valid.length - 1])}</b></div><svg viewBox="0 0 100 100" preserveAspectRatio="none"><polyline points={points} fill="none" stroke={color} strokeWidth="1.8" vectorEffect="non-scaling-stroke" /></svg><div className="chart-axis"><span>GEN 01</span><span>GEN {String(valid.length).padStart(2, "0")}</span></div></div>;
}

export function ValidationBadge({ result }: { result: FinalResult }) {
  return <div className={`validation-badge ${result.validation.collision_free ? "good" : "bad"}`}><i />{result.validation.collision_free ? "COLLISION FREE" : "COLLISIONS DETECTED"}</div>;
}
