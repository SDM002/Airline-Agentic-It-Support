"use client"

import Link from "next/link"
import { useState } from "react"
import { Check, ShieldAlert, X } from "lucide-react"
import { toast } from "sonner"
import { useSession } from "@/components/shell"
import { PriorityBadge } from "@/components/ticket-badges"
import { Button } from "@/components/ui/button"
import { decideApproval } from "@/lib/api"

/** Human-in-the-loop: the agent paused on request_approval and waits for this decision. */
export function ApprovalCard({ approval, onDecided }) {
  const { role } = useSession()
  const [busy, setBusy] = useState(false)
  const [comment, setComment] = useState("")
  const ticket = approval.ticket
  const tid = ticket.id.toLowerCase()

  async function decide(approve) {
    setBusy(true)
    try {
      await decideApproval(approval.id, approve, comment || null)
      toast[approve ? "success" : "info"](approve ? `${ticket.id}: approved — agent resumed` : `${ticket.id}: rejected — ticket closed`)
      onDecided()
    } catch (err) {
      toast.error(err.message)
      setBusy(false)
    }
  }

  return (
    <div className="rounded-md border border-destructive/40 bg-card p-6">
      <div className="flex flex-wrap items-center gap-2">
        <ShieldAlert className="size-4 text-destructive" />
        {role === "it_support" ? (
          <Link href={`/support/tickets/${ticket.id}`} data-testid={`approval-${tid}-link`} className="font-mono text-sm text-primary hover:underline">{ticket.id}</Link>
        ) : (
          <span className="font-mono text-sm text-primary">{ticket.id}</span>
        )}
        <PriorityBadge priority={ticket.priority} />
        <span className="text-xs text-muted-foreground">
          {ticket.requester_name} · {ticket.airport} · {approval.id}
        </span>
      </div>
      <p className="mt-3 text-heading">{ticket.title}</p>
      <div className="mt-4 rounded-md border border-slate-800 bg-terminal p-4 font-mono text-xs text-slate-200">
        <div className="text-amber-300">request_approval(</div>
        <div className="pl-4"><span className="text-slate-400">requested_access=</span>&quot;{approval.action}&quot;</div>
        <div className="pl-4"><span className="text-slate-400">reason=</span>&quot;{approval.reason}&quot;</div>
        <div className="text-amber-300">)</div>
      </div>
      <input
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Comment (optional, shown to the employee)"
        aria-label="Decision comment"
        data-testid={`comment-${tid}-input`}
        className="mt-4 w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-sky-600"
      />
      <div className="mt-4 flex gap-3">
        <Button disabled={busy} onClick={() => decide(true)} data-testid={`approve-${tid}-button`}>
          <Check /> Approve
        </Button>
        <Button variant="destructive" disabled={busy} onClick={() => decide(false)} data-testid={`reject-${tid}-button`}>
          <X /> Reject
        </Button>
      </div>
    </div>
  )
}
