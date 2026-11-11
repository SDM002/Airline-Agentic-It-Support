"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { TicketActions } from "@/components/ticket-actions"
import { PriorityBadge, SlaTimer } from "@/components/ticket-badges"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getMeta, listTickets } from "@/lib/api"

export default function TicketsPage() {
  const [tickets, setTickets] = useState(null)
  const [meta, setMeta] = useState({ statuses: [], teams: [] })
  const [team, setTeam] = useState("all")
  const [status, setStatus] = useState("active")
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    getMeta().then(setMeta)
    listTickets().then(setTickets)
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [])

  if (!tickets) return <p className="font-mono text-sm text-muted-foreground">loading queue…</p>

  const FILTERS = ["active", "all", ...meta.statuses]
  const replace = (t) => setTickets((all) => all.map((x) => (x.id === t.id ? t : x)))
  const rows = tickets.filter(
    (t) => (team === "all" || t.team === team) && (status === "all" || (status === "active" ? !["resolved", "closed"].includes(t.status) : t.status === status)),
  )

  return (
    <>
      <div className="mb-8 flex flex-wrap items-end gap-3">
        <div className="mr-auto">
          <p className="font-mono text-xs text-primary">{"// support"}</p>
          <h1 className="mt-1 text-3xl sm:text-4xl">
            Ticket queue <span className="font-mono text-base font-normal tracking-normal text-muted-foreground">({rows.length})</span>
          </h1>
        </div>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger data-testid="queue-status-filter" className="w-48"><SelectValue /></SelectTrigger>
          <SelectContent>
            {FILTERS.map((s) => <SelectItem key={s} value={s}>{s === "all" ? "All statuses" : s === "active" ? "Active (unresolved)" : s}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={team} onValueChange={setTeam}>
          <SelectTrigger data-testid="queue-team-filter" className="w-48"><SelectValue /></SelectTrigger>
          <SelectContent>
            {["all", ...meta.teams].map((t) => <SelectItem key={t} value={t}>{t === "all" ? "All teams" : t}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border border-border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="pl-6">Ticket</TableHead>
              <TableHead>Priority / Team</TableHead>
              <TableHead>Requester</TableHead>
              <TableHead>SLA</TableHead>
              <TableHead className="pr-6">Assign / Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((t) => (
                <TableRow key={t.id} className="align-top">
                  <TableCell className="max-w-md min-w-72 py-4 pl-6 whitespace-normal">
                    <div className="flex items-center gap-2 font-mono text-xs">
                      <Link
                        href={`/support/tickets/${t.id}`}
                        data-testid={`queue-ticket-${t.id.toLowerCase()}-link`}
                        className="rounded-sm text-primary outline-none hover:underline focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                      >
                        {t.id}
                      </Link>
                      <span className="text-muted-foreground">{t.airport} · {t.source}</span>
                    </div>
                    <p className="mt-1 text-heading">{t.title}</p>
                    <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">{t.description}</p>
                  </TableCell>
                  <TableCell className="py-4">
                    <PriorityBadge priority={t.priority} />
                    <p className="mt-1.5 text-xs text-muted-foreground">{t.team}</p>
                  </TableCell>
                  <TableCell className="py-4 text-xs">
                    <p className="text-heading">{t.requester_name}</p>
                    <p className="mt-1.5 text-muted-foreground">{t.category}</p>
                  </TableCell>
                  <TableCell className="py-4"><SlaTimer ticket={t} now={now} /></TableCell>
                  <TableCell className="py-4 pr-6">
                    <TicketActions ticket={t} onChange={replace} />
                  </TableCell>
                </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </>
  )
}
