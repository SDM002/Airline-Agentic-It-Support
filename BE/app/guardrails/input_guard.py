"""input_guard node: runs on every employee message before the agent sees it.

- Password / MFA code shared  -> message replaced, agent not called (blocked)
- Prompt injection            -> agent not called (blocked)
- Email / card number         -> redacted, agent continues
The employee's message is replaced in place (same id), so nothing sensitive is stored in the chat memory.
"""

from langchain.messages import AIMessage, HumanMessage

from app.agent.state import AgentState
from app.guardrails import rules


async def input_guard(state: AgentState) -> dict:
    message = state["messages"][-1]
    text = message.content

    if rules.SECRET_SHARED.search(text):
        return {
            "messages": [HumanMessage(rules.SECRET_REMOVED, id=message.id), AIMessage(rules.SECRET_REPLY)],
            "blocked": True,
            "guardrails": ["input: password or code removed, request blocked"],
        }

    if rules.PROMPT_INJECTION.search(text):
        return {
            "messages": [AIMessage(rules.INJECTION_REPLY)],
            "blocked": True,
            "guardrails": ["input: prompt injection blocked"],
        }

    redacted, found = rules.redact_pii(text)
    if found:
        return {
            "messages": [HumanMessage(redacted, id=message.id)],
            "blocked": False,
            "guardrails": [f"input: {', '.join(found)} redacted"],
        }

    return {"blocked": False, "guardrails": []}
