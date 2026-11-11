"use client"

import Link from "next/link"
import { useParams } from "next/navigation"
import { useCallback, useEffect, useState } from "react"
import { ArrowLeft, BookOpen, History, MessageSquareText, ScanSearch } from "lucide-react"
import { AgentTrace } from "@/components/agent-trace"
import { ApprovalCard } from "@/components/approval-card"
import { TicketActions } from "@/components/ticket-actions"
import { PriorityBadge, SlaTimer, StatusBadge } from "@/components/ticket-badges"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { getTicket, listApprovals } from "@/lib/api"

const time = (iso) => new Date(iso).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })

export default function TicketDetailPage() {
  const { id } = useParams()
  const [t, setT] = useState(undefined)
  const [approval, setApproval] = useState(null)
  const [now] = useState(() => Date.now())

  const load = useCallback(
    () =>
      getTicket(id)
        .then(async (ticket) => {
          const pending = ticket.status === "awaiting-approval" ? await listApprovals() : []
          setApproval(pending.find((a) => a.ticket_id === id) ?? null)
          setT(ticket)
        })
        .catch(() => setT(null)),
    [id],
  )

  useEffect(() => {
    load()
  }, [load])

  if (t === undefined) return <p className="font-mono text-sm text-muted-foreground">loading {id}…</p>
  if (t === null) return <p className="font-mono text-sm text-destructive">ticket {id} not found</p>

  return (
    <>
      <Link href="/support/tickets" data-testid="ticket-back-link" className="inline-flex items-center gap-1 rounded-sm text-sm text-muted-foreground outline-none hover:text-heading focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 focus-visible:ring-offset-background">
        <ArrowLeft className="size-4" /> Queue
      </Link>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <span className="font-mono text-sm text-primary">{t.id}</span>
        <PriorityBadge priority={t.priority} />
        <StatusBadge status={t.status} />
        <span className="font-mono text-xs text-muted-foreground">{t.assignee ?? "unassigned"}</span>
        <span className="ml-auto font-mono text-xs text-muted-foreground">SLA <SlaTimer ticket={t} now={now} /></span>
      </div>
      <h1 className="mt-3 text-3xl sm:text-4xl">{t.title}</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        {t.requester_name} ({t.requester_id}) · {t.airport} · via {t.source} · {t.team} · opened {time(t.created_at)}
      </p>
      <div className="mt-6">
        {/* load() refreshes the audit trail after every change */}
        <TicketActions ticket={t} onChange={load} full />
      </div>

      <div className="mt-10 grid gap-10 lg:grid-cols-[1.5fr_1fr]">
        <Tabs defaultValue="details" className="min-w-0">
          <TabsList>
            <TabsTrigger value="details" data-testid="tab-details"><ScanSearch /> Details</TabsTrigger>
            <TabsTrigger value="knowledge" data-testid="tab-knowledge"><BookOpen /> Knowledge</TabsTrigger>
            <TabsTrigger value="comments" data-testid="tab-comments"><MessageSquareText /> Comments ({t.comments.length})</TabsTrigger>
            <TabsTrigger value="audit" data-testid="tab-audit"><History /> Audit trail</TabsTrigger>
          </TabsList>

          <TabsContent value="details" className="space-y-6">
            <p className="whitespace-pre-wrap text-heading">{t.description}</p>
            <dl className="grid grid-cols-2 border-t border-l border-border sm:grid-cols-4">
              {[["Category", t.category], ["Priority", t.priority], ["Team", t.team], ["SLA", `${t.sla_hours} h`]].map(([k, v]) => (
                <div key={k} className="border-r border-b border-border bg-card p-4">
                  <dt className="text-xs text-muted-foreground">{k}</dt>
                  <dd className="mt-1 font-mono text-heading">{v}</dd>
                </div>
              ))}
            </dl>
          </TabsContent>

          <TabsContent value="knowledge" className="space-y-8">
            <section>
              <h3 className="text-lg">Matching SOPs <span className="font-mono text-xs font-normal text-muted-foreground">(Pinecone · reranked)</span></h3>
              <ul className="mt-3 space-y-2">
                {t.sops.map((s, i) => (
                  <li key={i} className="rounded-md border border-border bg-card p-4">
                    <div className="flex items-center gap-3 font-mono text-xs">
                      <span className="text-primary">{s.section}</span>
                      <span className="ml-auto text-muted-foreground">score {s.score}</span>
                    </div>
                    <p className="mt-1 font-mono text-xs text-muted-foreground">{s.source}</p>
                    <p className="mt-2 line-clamp-6 text-sm whitespace-pre-wrap text-muted-foreground">{s.text}</p>
                  </li>
                ))}
              </ul>
            </section>
            <section>
              <h3 className="text-lg">Similar tickets</h3>
              <ul className="mt-3 space-y-2">
                {t.similar.map((s) => (
                  <li key={s.id} className="flex flex-wrap items-center gap-3 rounded-md border border-border bg-card p-4">
                    <Link href={`/support/tickets/${s.id}`} data-testid={`similar-${s.id.toLowerCase()}-link`} className="font-mono text-xs text-primary hover:underline">{s.id}</Link>
                    <span className="min-w-0 flex-1 text-heading">{s.title}</span>
                    <span className="font-mono text-xs text-muted-foreground">{s.airport}</span>
                    <StatusBadge status={s.status} />
                  </li>
                ))}
              </ul>
            </section>
          </TabsContent>

          <TabsContent value="comments">
            {t.comments.length === 0 && <p className="text-muted-foreground">No comments yet.</p>}
            <ul className="space-y-3">
              {t.comments.map((c, i) => (
                <li key={i} className="rounded-md border border-border bg-card p-4">
                  <div className="font-mono text-xs text-muted-foreground">{time(c.created_at)} · {c.author}</div>
                  <p className="mt-1 text-heading">{c.text}</p>
                </li>
              ))}
            </ul>
          </TabsContent>

          <TabsContent value="audit">
            <ol className="border-l border-border">
              {t.audit.map((a, i) => (
                <li key={i} className="relative pb-6 pl-6 last:pb-0">
                  <span className="absolute top-1.5 -left-[4.5px] size-2 rounded-full bg-primary" />
                  <div className="font-mono text-xs text-muted-foreground">{time(a.at)} · {a.actor}</div>
                  <div className="mt-0.5 text-heading">{a.event}</div>
                </li>
              ))}
            </ol>
          </TabsContent>
        </Tabs>

        <aside className="min-w-0 space-y-6">
          <AgentTrace trace={t.trace} ticketId={t.id} />
          {approval && <ApprovalCard approval={approval} onDecided={load} />}
        </aside>
      </div>
    </>
  )
}
