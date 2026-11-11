"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { AlertTriangle, ArrowRight, CircleDot, Loader, MessageSquare, ShieldAlert, UserX } from "lucide-react"
import { PriorityBadge, SlaTimer, StatusBadge, slaRemaining } from "@/components/ticket-badges"
import { getMeta, listTickets } from "@/lib/api"

const cell = "border-r border-b border-border bg-card p-6"
const link = "rounded-sm outline-none focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 focus-visible:ring-offset-background"

export default function DashboardPage() {
  const [tickets, setTickets] = useState(null)
  const [teams, setTeams] = useState([])
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    getMeta().then((m) => setTeams(m.teams))
    listTickets().then(setTickets)
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [])

  if (!tickets) return <p className="font-mono text-sm text-muted-foreground">loading…</p>

  const active = tickets.filter((t) => !["resolved", "closed"].includes(t.status))
  const awaiting = tickets.filter((t) => t.status === "awaiting-approval")
  const urgent = [...active].sort((a, b) => slaRemaining(a, now) - slaRemaining(b, now)).slice(0, 8)
  const fromChat = tickets.filter((t) => t.source === "chat").slice(0, 5)
  const counters = [
    ["Open", tickets.filter((t) => t.status === "open").length, CircleDot],
    ["In progress", tickets.filter((t) => t.status === "in-progress").length, Loader],
    ["Unassigned", active.filter((t) => !t.assignee).length, UserX],
    ["SLA breached", active.filter((t) => slaRemaining(t, now) < 0).length, AlertTriangle, true],
  ]

  return (
    <>
      <p className="font-mono text-xs text-primary">{"// support"}</p>
      <h1 className="mt-1 mb-8 text-3xl sm:text-4xl">Dashboard</h1>

      <div className="grid grid-cols-2 border-t border-l border-border lg:grid-cols-4">
        {counters.map(([label, value, Icon, alert]) => (
          <div key={label} data-testid={`counter-${label.toLowerCase().replace(" ", "-")}`} className={cell}>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Icon className={alert && value ? "size-4 text-destructive" : "size-4"} /> {label}
            </div>
            <div className={`mt-3 font-heading text-4xl font-bold tracking-tighter ${alert && value ? "text-destructive" : "text-heading"}`}>{value}</div>
          </div>
        ))}

        <section className={`${cell} col-span-2 min-w-0 lg:col-span-3`}>
          <div className="flex items-center justify-between">
            <h2 className="text-xl">Closest to SLA breach</h2>
            <Link href="/support/tickets" data-testid="dashboard-all-tickets-link" className={`flex items-center gap-1 text-sm text-primary hover:underline ${link}`}>
              All tickets <ArrowRight className="size-4" />
            </Link>
          </div>
          <ul className="mt-4 divide-y divide-border">
            {urgent.map((t) => (
              <li key={t.id} className="flex items-center gap-3 py-2.5 text-sm">
                <Link href={`/support/tickets/${t.id}`} data-testid={`dashboard-ticket-${t.id.toLowerCase()}-link`} className={`font-mono text-xs text-primary hover:underline ${link}`}>{t.id}</Link>
                <PriorityBadge priority={t.priority} />
                <span className="min-w-0 flex-1 truncate text-heading">{t.title}</span>
                <span className="hidden sm:inline"><StatusBadge status={t.status} /></span>
                <SlaTimer ticket={t} now={now} />
              </li>
            ))}
          </ul>
        </section>

        <aside className={`${cell} col-span-2 lg:col-span-1`}>
          <h2 className="flex items-center gap-2 text-xl"><ShieldAlert className="size-5 text-destructive" /> Awaiting approval</h2>
          <div className="mt-3 font-heading text-5xl font-bold tracking-tighter text-heading">{awaiting.length}</div>
          <p className="mt-1 text-xs text-muted-foreground">Agent paused on sensitive actions.</p>
          <ul className="mt-4 space-y-1.5 text-sm">
            {awaiting.slice(0, 4).map((t) => (
              <li key={t.id} className="truncate"><span className="font-mono text-xs text-primary">{t.id}</span> {t.title}</li>
            ))}
          </ul>
          <Link href="/support/approvals" data-testid="dashboard-approvals-link" className={`mt-5 flex items-center gap-1 text-sm text-primary hover:underline ${link}`}>
            Review approvals <ArrowRight className="size-4" />
          </Link>
        </aside>

        <section className={`${cell} col-span-2`}>
          <h2 className="flex items-center gap-2 text-xl"><MessageSquare className="size-5 text-primary" /> New from chat</h2>
          <ul className="mt-4 divide-y divide-border">
            {fromChat.map((t) => (
              <li key={t.id} className="py-2.5 text-sm">
                <Link href={`/support/tickets/${t.id}`} data-testid={`chat-ticket-${t.id.toLowerCase()}-link`} className={`font-mono text-xs text-primary hover:underline ${link}`}>{t.id}</Link>
                <span className="ml-2 text-heading">{t.title}</span>
                <p className="mt-0.5 text-xs text-muted-foreground">{t.requester_name} · {t.airport}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className={`${cell} col-span-2`}>
          <h2 className="text-xl">Open load by team</h2>
          <dl className="mt-4 divide-y divide-border">
            {teams.map((team) => (
              <div key={team} className="flex items-baseline justify-between py-2.5 text-sm">
                <dt className="text-muted-foreground">{team}</dt>
                <dd className="font-mono text-heading">{active.filter((t) => t.team === team).length}</dd>
              </div>
            ))}
          </dl>
        </section>
      </div>
    </>
  )
}
