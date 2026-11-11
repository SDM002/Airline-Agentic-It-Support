"use client"

import { useCallback, useEffect, useState } from "react"
import { CheckCheck } from "lucide-react"
import { toast } from "sonner"
import { ApprovalCard } from "@/components/approval-card"
import { useSession } from "@/components/shell"
import { listApprovals } from "@/lib/api"

export default function ApprovalsPage() {
  const { role } = useSession()
  const [items, setItems] = useState(null)
  const load = useCallback(() => listApprovals().then(setItems).catch((e) => toast.error(e.message)), [])

  useEffect(() => {
    load()
  }, [load])

  return (
    <>
      <p className="font-mono text-xs text-primary">{role === "manager" ? "// manager" : "// support"}</p>
      <h1 className="mt-1 text-3xl sm:text-4xl">Approvals</h1>
      <p className="mt-2 max-w-2xl text-muted-foreground">
        {role === "manager"
          ? "Access requests from your team. The agent paused and will continue once you decide."
          : "The agent paused on these access requests. Only the requester's line manager or IAM can decide (policy IT-POL-002)."}
      </p>

      {!items && <p className="mt-8 font-mono text-sm text-muted-foreground">loading…</p>}
      {items?.length === 0 && (
        <p className="mt-8 flex items-center gap-2 text-muted-foreground"><CheckCheck className="size-5 text-success" /> Nothing waiting. All clear.</p>
      )}
      <div className="mt-8 grid gap-4 lg:grid-cols-2">
        {items?.map((a) => <ApprovalCard key={a.id} approval={a} onDecided={load} />)}
      </div>
    </>
  )
}
