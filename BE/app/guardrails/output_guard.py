"""output_guard node: checks the agent's final reply before the employee sees it.
Replaces requests for secrets, removes [IT only] steps, redacts PII; the reply is replaced in place in the chat memory.
"""

from langchain.messages import AIMessage

from app.agent.state import AgentState
from app.guardrails import rules


# Clean the agent's final reply and record which rules fired
async def output_guard(state: AgentState) -> dict:
    reply = state["messages"][-1]
    text = reply.content
    triggered = []

    # Agent asked for a password or code: replace the whole reply
    if rules.ASKS_FOR_SECRET.search(text):
        text = rules.SAFE_REPLY
        triggered.append("output: request for password or code replaced")

    # Remove lines with IT-only steps
    lines = text.splitlines()
    kept = [line for line in lines if not rules.IT_ONLY_STEP.search(line)]
    if len(kept) < len(lines):
        text = "\n".join(kept)
        triggered.append(f"output: {len(lines) - len(kept)} IT-only step(s) removed")

    # Redact emails and card numbers
    text, found = rules.redact_pii(text)
    if found:
        triggered.append(f"output: {', '.join(found)} redacted")

    return {
        "messages": [AIMessage(text, id=reply.id)],
        "guardrails": state.get("guardrails", []) + triggered,
    }
