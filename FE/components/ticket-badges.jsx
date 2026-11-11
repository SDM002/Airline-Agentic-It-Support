import { cn } from "@/lib/utils"
const STATUS = {
  open: "border-primary/40 text-primary",
  "in-progress": "border-amber-400/40 text-amber-700",
  "awaiting-approval": "border-destructive/50 text-destructive",
  resolved: "border-success/40 text-success",
  closed: "border-border text-muted-foreground",
}
const PRIORITY = {
  P1: "bg-destructive/15 text-destructive",
  P2: "bg-amber-400/10 text-amber-700",
  P3: "bg-slate-900/5 text-slate-700",
  P4: "bg-slate-900/5 text-muted-foreground",
}
export function StatusBadge({ status }) {
  return (
    <span
      className={cn("inline-flex rounded-sm border px-2 py-0.5 font-mono text-xs whitespace-nowrap", STATUS[status])}
    >
      {status}
    </span>
  )
}
export function PriorityBadge({ priority }) {
  return (
    <span className={cn("inline-flex rounded-sm px-1.5 py-0.5 font-mono text-xs font-medium", PRIORITY[priority])}>
      {priority}
    </span>
  )
}

export function slaRemaining(t, now) {
  return Date.parse(t.created_at) + t.sla_hours * 3_600_000 - now
}

export function SlaTimer({ ticket, now }) {
  if (["resolved", "closed"].includes(ticket.status)) return <span className="font-mono text-xs text-success">met</span>
  const ms = slaRemaining(ticket, now)
  const abs = Math.abs(ms)
  const hh = String(Math.floor(abs / 3_600_000)).padStart(2, "0")
  const mm = String(Math.floor((abs % 3_600_000) / 60_000)).padStart(2, "0")
  const ss = String(Math.floor((abs % 60_000) / 1000)).padStart(2, "0")
  const tone = ms < 0 ? "text-destructive" : ms < 3_600_000 ? "text-amber-700" : "text-slate-700"
  return (
    <span className={cn("font-mono text-xs tabular-nums", tone)}>
      {ms < 0 ? "-" : ""}
      {hh}:{mm}:{ss}
    </span>
  )
}
