"""input_guard node: checks every employee message before the agent sees it.
Blocks passwords and prompt injection, redacts PII; the message is replaced in place so nothing sensitive is stored.
"""

from langchain.messages import AIMessage, HumanMessage

from app.agent.state import AgentState
from app.guardrails import rules


# Block, redact or pass the latest employee message
async def input_guard(state: AgentState) -> dict:
    message = state["messages"][-1]
    text = message.content

    # Password or code shared: remove it and stop
    if rules.SECRET_SHARED.search(text):
        return {
            "messages": [HumanMessage(rules.SECRET_REMOVED, id=message.id), AIMessage(rules.SECRET_REPLY)],
            "blocked": True,
            "guardrails": ["input: password or code removed, request blocked"],
        }

    # Prompt injection: stop
    if rules.PROMPT_INJECTION.search(text):
        return {
            "messages": [AIMessage(rules.INJECTION_REPLY)],
            "blocked": True,
            "guardrails": ["input: prompt injection blocked"],
        }

    # Email or card number: redact and continue
    redacted, found = rules.redact_pii(text)
    if found:
        return {
            "messages": [HumanMessage(redacted, id=message.id)],
            "blocked": False,
            "guardrails": [f"input: {', '.join(found)} redacted"],
        }

    return {"blocked": False, "guardrails": []}
