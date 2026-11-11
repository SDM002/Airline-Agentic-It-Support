"use client"

import { useEffect, useState } from "react"
import { Check, Lock } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getMeta, updateTicket } from "@/lib/api"

/** Assign to L1/L2 and change status. `full` adds explicit Resolve / Close buttons. */
export function TicketActions({ ticket, onChange, full = false }) {
  const tid = ticket.id.toLowerCase()
  const [statuses, setStatuses] = useState([])

  useEffect(() => {
    getMeta().then((m) => setStatuses(m.statuses))
  }, [])

  async function patch(p, msg) {
    try {
      onChange(await updateTicket(ticket.id, p))
      toast.success(`${ticket.id}: ${msg}`)
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Select value={ticket.assignee ?? ""} onValueChange={(v) => patch({ assignee: v }, `assigned to ${v}`)}>
        <SelectTrigger size="sm" className="w-32" aria-label="Assign" data-testid={`assign-${tid}-select`}>
          <SelectValue placeholder="Unassigned" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="L1">L1 support</SelectItem>
          <SelectItem value="L2">L2 support</SelectItem>
        </SelectContent>
      </Select>
      <Select value={ticket.status} onValueChange={(v) => patch({ status: v }, `status → ${v}`)}>
        <SelectTrigger size="sm" className="w-44" aria-label="Status" data-testid={`status-${tid}-select`}>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {statuses.map((s) => (
            // Only the approval flow may enter awaiting-approval.
            <SelectItem key={s} value={s} disabled={s === "awaiting-approval"}>
              {s}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {full && (
        <>
          <Button size="sm" disabled={ticket.status === "resolved" || ticket.status === "closed"} onClick={() => patch({ status: "resolved" }, "resolved")} data-testid="resolve-ticket-button">
            <Check /> Resolve
          </Button>
          <Button size="sm" variant="outline" disabled={ticket.status === "closed"} onClick={() => patch({ status: "closed" }, "closed")} data-testid="close-ticket-button">
            <Lock /> Close
          </Button>
        </>
      )}
    </div>
  )
}
