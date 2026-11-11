/** Terminal-style list of the tools the agent called in the chat that created this ticket. */
export function AgentTrace({ trace, ticketId }) {
  return (
    <div className="scanlines overflow-hidden rounded-md border border-slate-800 bg-terminal text-slate-200">
      <div className="flex items-center gap-2 border-b border-slate-800 px-4 py-2 font-mono text-xs text-slate-400">
        <span className="size-2 rounded-full bg-emerald-400" />
        agent-trace · {ticketId}
      </div>
      <ol className="space-y-3 p-4 font-mono text-xs leading-relaxed">
        {trace.length === 0 && <li className="text-slate-400"># not created by the agent (no chat trace)</li>}
        {trace.map((t, i) => (
          <li
            key={i}
            className="animate-in fade-in slide-in-from-bottom-1 fill-mode-both duration-500 motion-reduce:animate-none"
            style={{ animationDelay: `${i * 220}ms` }}
          >
            <span className="text-slate-400">$ </span>
            <span className={t.tool === "request_approval" ? "text-emerald-400" : "text-amber-300"}>{t.tool}</span>
            {Object.entries(t.args).map(([k, v]) => (
              <div key={k} className="pl-4 break-words text-gray-300">
                <span className="text-slate-400">{k}=</span>&quot;{String(v)}&quot;
              </div>
            ))}
          </li>
        ))}
        <li className="text-slate-400">
          <span className="animate-pulse motion-reduce:animate-none">▍</span>
        </li>
      </ol>
    </div>
  )
}
