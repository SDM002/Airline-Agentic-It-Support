"""output_guard node: checks the agent's final reply before the employee sees it.

- Asks the employee for a password / MFA code -> whole reply replaced with a safe message
- Contains [IT only] steps                     -> those lines removed
- Contains an email / card number              -> redacted
The reply is replaced in place (same id) in the chat memory.
"""

from langchain.messages import AIMessage

from app.agent.state import AgentState
from app.guardrails import rules


async def output_guard(state: AgentState) -> dict:
    reply = state["messages"][-1]
    text = reply.content
    triggered = []

    if rules.ASKS_FOR_SECRET.search(text):
        text = rules.SAFE_REPLY
        triggered.append("output: request for password or code replaced")

    lines = text.splitlines()
    kept = [line for line in lines if not rules.IT_ONLY_STEP.search(line)]
    if len(kept) < len(lines):
        text = "\n".join(kept)
        triggered.append(f"output: {len(lines) - len(kept)} IT-only step(s) removed")

    text, found = rules.redact_pii(text)
    if found:
        triggered.append(f"output: {', '.join(found)} redacted")

    return {
        "messages": [AIMessage(text, id=reply.id)],
        "guardrails": state.get("guardrails", []) + triggered,
    }
