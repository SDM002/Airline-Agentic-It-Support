"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import Markdown from "react-markdown"
import { Bot, Hourglass, MessageSquarePlus, Send } from "lucide-react"
import { toast } from "sonner"
import { LiveSteps, StepPanels } from "@/components/agent-steps"
import { useSession } from "@/components/shell"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { getConversation, listConversations, streamMessage } from "@/lib/api"
import { cn } from "@/lib/utils"

const fade = "animate-in fade-in slide-in-from-bottom-1 fill-mode-both duration-500 motion-reduce:animate-none"
const newChat = () => ({ id: null, messages: [], awaiting: [] })
const time = (iso) => new Date(iso).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })

/** Applies one streamed agent event to the agent's reply that is being built. */
function applyEvent(turn, e) {
  if (e.type === "classified") {
    const { type, ...analysis } = e
    return { ...turn, analysis, steps: [...turn.steps, { tool: "classify", args: null, result: analysis }] }
  }
  if (e.type === "knowledge") return { ...turn, steps: [...turn.steps, { tool: "rag", args: null, result: e.results }] }
  if (e.type === "guardrail") return { ...turn, steps: [...turn.steps, { tool: "guardrail", args: null, result: e.rule }] }
  if (e.type === "tool_call") return { ...turn, steps: [...turn.steps, { tool: e.tool, args: e.args, result: null }] }
  if (e.type === "tool_result") {
    const i = turn.steps.findLastIndex((s) => s.tool === e.tool && s.result === null)
    return { ...turn, steps: turn.steps.map((s, j) => (j === i ? { ...s, result: e.result } : s)) }
  }
  if (e.type === "approval") {
    // The graph paused inside request_approval, so that step has no result yet
    const waiting = { approval_id: e.approval_id, ticket_id: e.ticket_id, status: "waiting for manager / IAM" }
    return { ...turn, text: e.message, steps: turn.steps.map((s) => (s.tool === "request_approval" && s.result === null ? { ...s, result: waiting } : s)) }
  }
  if (e.type === "answer") return { ...turn, text: e.text }
  if (e.type === "error") return { ...turn, text: e.message }
  return turn
}

export default function ChatPage() {
  const { name } = useSession()
  const [history, setHistory] = useState([])
  const [chat, setChat] = useState(newChat)
  const [text, setText] = useState("")
  const [busy, setBusy] = useState(false)

  const refreshHistory = () => listConversations().then(setHistory).catch((e) => toast.error(e.message))

  useEffect(() => {
    refreshHistory()
  }, [])

  async function open(id) {
    const c = await getConversation(id)
    setChat({ id: c.id, messages: c.messages, awaiting: c.awaiting_approval })
  }

  // The agent reply is always the last message while streaming
  const updateReply = (fn) => setChat((c) => ({ ...c, messages: [...c.messages.slice(0, -1), fn(c.messages.at(-1))] }))

  async function send(e) {
    e.preventDefault()
    const message = text.trim()
    if (!message || busy) return
    setText("")
    setBusy(true)
    setChat((c) => ({
      ...c,
      messages: [...c.messages, { from: "user", text: message }, { from: "agent", text: "", steps: [], analysis: null, live: true }],
    }))
    try {
      await streamMessage(message, chat.id, (event) => {
        if (event.type === "start") setChat((c) => ({ ...c, id: event.thread_id }))
        if (event.type === "approval") setChat((c) => ({ ...c, awaiting: [event] }))
        if (event.type === "error") toast.error(event.message)
        updateReply((turn) => applyEvent(turn, event))
      })
      refreshHistory()
    } catch (err) {
      toast.error(err.message)
      updateReply((turn) => ({ ...turn, text: err.message }))
    }
    updateReply((turn) => ({ ...turn, live: false }))
    setBusy(false)
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
      <aside className="order-last lg:order-none">
        <Button variant="outline" className="w-full justify-start" onClick={() => setChat(newChat())} data-testid="chat-new-button">
          <MessageSquarePlus /> New chat
        </Button>
        <h2 className="mt-6 mb-2 font-mono text-xs font-normal tracking-normal text-muted-foreground">history</h2>
        <ul className="space-y-1 lg:max-h-[calc(100dvh-14rem)] lg:overflow-auto">
          {history.map((c) => (
            <li key={c.id}>
              <button
                onClick={() => open(c.id)}
                data-testid={`chat-history-${c.id}-button`}
                className={cn(
                  "w-full rounded-md px-3 py-2 text-left text-sm transition-colors duration-200 outline-none hover:bg-card focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 focus-visible:ring-offset-background",
                  c.id === chat.id ? "bg-card text-heading" : "text-muted-foreground",
                )}
              >
                <span className="line-clamp-1">{c.title}</span>
                <span className="font-mono text-xs text-muted-foreground">{time(c.updated_at)}</span>
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <section>
        <h1 className="text-3xl sm:text-4xl">Hi {name.split(" ")[0]}, what&apos;s not working?</h1>
        <p className="mt-2 text-muted-foreground">Describe it like you&apos;d tell a colleague. I&apos;ll suggest a fix from our SOPs first, and open a ticket if it doesn&apos;t work.</p>

        <div className="mt-8 rounded-md border border-border bg-card">
          <div className="min-h-72 space-y-5 p-6" aria-live="polite">
            {chat.messages.length === 0 && <p className="text-sm text-muted-foreground">Start by describing your IT problem below.</p>}

            {chat.messages.map((m, i) =>
              m.from === "user" ? (
                <p key={i} className="ml-auto w-fit max-w-[85%] rounded-md bg-muted px-4 py-2 whitespace-pre-wrap text-heading">{m.text}</p>
              ) : (
                <div key={i} className="space-y-3">
                  {m.live && <LiveSteps steps={m.steps} />}
                  {m.text && (
                    <div className={cn("flex gap-3", fade)}>
                      <Bot className="mt-0.5 size-5 shrink-0 text-primary" />
                      <div className="min-w-0 space-y-2 text-sm leading-relaxed [&_ol]:list-decimal [&_ol]:pl-5 [&_strong]:text-heading [&_ul]:list-disc [&_ul]:pl-5">
                        <Markdown>{m.text}</Markdown>
                      </div>
                    </div>
                  )}
                  {!m.live && m.steps && <StepPanels analysis={m.analysis} steps={m.steps} />}
                </div>
              ),
            )}

            {chat.awaiting.length > 0 && !busy && (
              <div className={cn("ml-8 flex max-w-md gap-3 rounded-md border border-amber-400/50 bg-muted p-4 text-sm", fade)}>
                <Hourglass className="size-4 shrink-0 text-amber-700" />
                <div>
                  <p className="text-heading">Waiting for approval</p>
                  <p className="mt-1 text-muted-foreground">
                    {chat.awaiting[0].requested_access} · ticket <span className="font-mono">{chat.awaiting[0].ticket_id}</span>. Your manager or IAM will decide.
                  </p>
                  <Link href="/employee/my-tickets" data-testid="chat-view-tickets-link" className="mt-2 inline-block text-xs text-primary hover:underline">View my tickets →</Link>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={send} className="flex items-end gap-3 border-t border-border p-4">
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send(e)}
              placeholder={chat.messages.length ? "Reply, e.g. \"still not working\"" : "e.g. Boarding pass printer at counter 4 isn't printing"}
              aria-label="Message the helpdesk agent"
              data-testid="chat-issue-input"
              disabled={busy}
              className="max-h-40 resize-none border-0 bg-transparent! focus-visible:ring-0 focus-visible:ring-offset-0"
            />
            <Button type="submit" disabled={busy || !text.trim()} data-testid="chat-send-button"><Send /> Send</Button>
          </form>
        </div>
      </section>
    </div>
  )
}
