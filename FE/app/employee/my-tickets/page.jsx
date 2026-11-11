"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { MessageSquarePlus } from "lucide-react"
import { PriorityBadge, StatusBadge } from "@/components/ticket-badges"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { listMyTickets } from "@/lib/api"

const FRIENDLY = {
  open: "We've got it — waiting for an engineer.",
  "in-progress": "An engineer is working on it.",
  "awaiting-approval": "Waiting for your manager or IAM to approve.",
  resolved: "Fixed. Reply in chat if it comes back.",
  closed: "Closed.",
}

export default function MyTicketsPage() {
  const [tickets, setTickets] = useState(null)

  useEffect(() => {
    listMyTickets().then(setTickets)
  }, [])

  const done = (t) => ["resolved", "closed"].includes(t.status)
  const groups = { active: tickets?.filter((t) => !done(t)) ?? [], done: tickets?.filter(done) ?? [] }

  return (
    <div className="max-w-3xl">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl">My tickets</h1>
          <p className="mt-2 text-muted-foreground">Everything you&apos;ve reported, and where it stands.</p>
        </div>
        <Button asChild data-testid="my-tickets-new-chat-button">
          <Link href="/employee/chat"><MessageSquarePlus /> Report an issue</Link>
        </Button>
      </div>

      <Tabs defaultValue="active" className="mt-8">
        <TabsList>
          <TabsTrigger value="active" data-testid="my-tickets-active-tab">Active ({groups.active.length})</TabsTrigger>
          <TabsTrigger value="done" data-testid="my-tickets-done-tab">Resolved ({groups.done.length})</TabsTrigger>
        </TabsList>
        {Object.entries(groups).map(([key, list]) => (
          <TabsContent key={key} value={key}>
            {!tickets && <p className="font-mono text-sm text-muted-foreground">loading…</p>}
            {tickets && list.length === 0 && <p className="text-muted-foreground">Nothing here.</p>}
            <ul className="space-y-3">
              {list.map((t) => (
                <li key={t.id} data-testid={`my-ticket-${t.id.toLowerCase()}`} className="rounded-md border border-border bg-card p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs text-muted-foreground">{t.id}</span>
                    <PriorityBadge priority={t.priority} />
                    <span className="ml-auto"><StatusBadge status={t.status} /></span>
                  </div>
                  <p className="mt-2 text-heading">{t.title}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{FRIENDLY[t.status]}</p>
                  <p className="mt-3 font-mono text-xs text-muted-foreground">
                    {t.team}{t.assignee ? ` · ${t.assignee}` : ""} · {new Date(t.created_at).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}
                  </p>
                </li>
              ))}
            </ul>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}
