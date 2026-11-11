import { Bot, Check, ChevronRight, Loader2, ScanSearch } from "lucide-react"
import { PriorityBadge } from "@/components/ticket-badges"
import { cn } from "@/lib/utils"

// What each agent step is called on screen, and where its data comes from
const LABEL = {
  guardrail: "Guardrail",
  classify: "Classifying issue",
  rag: "Searching knowledge base · Pinecone",
  search_knowledge_base: "Searching knowledge base again · Pinecone",
  get_employee_profile: "Reading employee profile · MongoDB",
  find_similar_tickets: "Checking similar tickets · MongoDB",
  create_ticket: "Creating ticket · MongoDB",
  assign_ticket: "Assigning ticket · MongoDB",
  update_ticket: "Updating ticket · MongoDB",
  get_ticket_status: "Looking up ticket status · MongoDB",
  request_approval: "Requesting approval · paused for a human",
}

const fade = "animate-in fade-in slide-in-from-bottom-1 fill-mode-both duration-300 motion-reduce:animate-none"

/** One-line result shown next to a finished step. */
function summary(step) {
  const r = step.result
  if (step.tool === "guardrail") return r
  if (step.tool === "classify") return `${r.category} · ${r.priority} · ${r.team} · ${r.airport}`
  if (step.tool === "rag" || step.tool === "search_knowledge_base") {
    const results = step.tool === "rag" ? r : r.results
    return results.map((k) => `${k.section.split(" — ")[0]} (${k.score})`).join(", ")
  }
  if (step.tool === "find_similar_tickets") return `${r.count} found: ${r.tickets.filter((t) => t.status === "open").length} open`
  if (step.tool === "get_employee_profile") return `${r.name} · ${r.department} · manager ${r.manager_id}`
  if (step.tool === "create_ticket") return `${r.ticket_id} · SLA ${r.sla_hours} h`
  if (step.tool === "assign_ticket") return `${r.team} · ${r.assignee}`
  if (step.tool === "update_ticket" || step.tool === "get_ticket_status") return `${r.ticket_id} · ${r.status}`
  if (step.tool === "request_approval") return `${r.approval_id} · ${r.status ?? "waiting"}`
  return ""
}

/** Live progress while the agent works: finished steps get a tick, the running one a spinner. */
export function LiveSteps({ steps }) {
  const running = steps.length === 0 || steps.at(-1).result !== null
  return (
    <ol className="ml-8 space-y-1.5 font-mono text-xs" aria-live="polite">
      {steps.map((s, i) => (
        <li key={i} className={cn("flex gap-2", fade)}>
          {s.result === null ? <Loader2 className="size-3.5 shrink-0 animate-spin text-primary" /> : <Check className="size-3.5 shrink-0 text-success" />}
          <span className="text-heading">{LABEL[s.tool] ?? s.tool}</span>
          {s.result !== null && <span className="min-w-0 truncate text-muted-foreground">{summary(s)}</span>}
        </li>
      ))}
      {running && (
        <li className={cn("flex gap-2 text-muted-foreground", fade)}>
          <Loader2 className="size-3.5 animate-spin text-primary" /> {steps.length ? "Thinking about the next step…" : "Classifying issue…"}
        </li>
      )}
    </ol>
  )
}

const panel =
  "ml-8 rounded-md border border-border bg-background [&[open]>summary>svg]:rotate-90"
const panelTitle = "flex cursor-pointer list-none items-center gap-2 px-4 py-2.5 text-sm text-heading select-none"

/** After the answer: the two collapsible panels (issue analysis + every agent step with its data). */
export function StepPanels({ analysis, steps }) {
  return (
    <div className="space-y-2">
      {analysis && (
        <details className={panel} data-testid="panel-issue-analysis">
          <summary className={panelTitle}>
            <ChevronRight className="size-4 transition-transform" /> <ScanSearch className="size-4 text-primary" /> Issue analysis
          </summary>
          <div className="border-t border-border px-4 py-3 text-sm">
            <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[["Category", analysis.category], ["Priority", <PriorityBadge key="p" priority={analysis.priority} />], ["Team", analysis.team], ["Airport", analysis.airport]].map(([k, v]) => (
                <div key={k}>
                  <dt className="text-xs text-muted-foreground">{k}</dt>
                  <dd className="mt-0.5 text-heading">{v}</dd>
                </div>
              ))}
            </dl>
            <p className="mt-3 text-muted-foreground">{analysis.reason}</p>
          </div>
        </details>
      )}

      {steps.length > 0 && (
        <details className={panel} data-testid="panel-agent-steps">
          <summary className={panelTitle}>
            <ChevronRight className="size-4 transition-transform" /> <Bot className="size-4 text-primary" /> Agent steps ({steps.length})
          </summary>
          <ol className="space-y-4 border-t border-border px-4 py-3">
            {steps.map((s, i) => (
              <li key={i} className="text-xs">
                <div className="flex gap-2 font-mono">
                  <span className="text-primary">{String(i + 1).padStart(2, "0")}</span>
                  <span className="text-heading">{LABEL[s.tool] ?? s.tool}</span>
                </div>
                {s.tool === "rag" ? (
                  <ul className="mt-2 space-y-2 pl-6">
                    {/* one SOP section can come back as several chunks, so the section name is not unique */}
                    {s.result.map((k, j) => (
                      <li key={j} className="rounded-sm bg-muted p-2">
                        <div className="flex gap-2 font-mono">
                          <span className="text-heading">{k.section}</span>
                          <span className="ml-auto text-muted-foreground">score {k.score}</span>
                        </div>
                        <div className="font-mono text-muted-foreground">{k.source}</div>
                        <p className="mt-1 line-clamp-4 whitespace-pre-wrap text-muted-foreground">{k.text}</p>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="mt-1 grid gap-1 pl-6 font-mono">
                    {s.args && <pre className="overflow-x-auto rounded-sm bg-terminal p-2 text-slate-200">{JSON.stringify(s.args, null, 2)}</pre>}
                    {s.result !== null && s.tool !== "classify" && s.tool !== "guardrail" && (
                      <pre className="max-h-48 overflow-auto rounded-sm bg-muted p-2 text-muted-foreground">{JSON.stringify(s.result, null, 2)}</pre>
                    )}
                    {(s.tool === "classify" || s.tool === "guardrail") && <p className="text-muted-foreground">{summary(s)}</p>}
                  </div>
                )}
              </li>
            ))}
          </ol>
        </details>
      )}
    </div>
  )
}
