"""resolve_issue node: the LLM decides the next step (reply, or call a tool) using the classification and the RAG results."""

from pathlib import Path

from langchain.messages import SystemMessage

from app.agent.state import AgentState
from app.core.llm_client import llm
from app.tools import TOOLS

PROMPT = (Path(__file__).parents[2] / "prompts" / "resolve_issue.txt").read_text()

agent_llm = llm.bind_tools(TOOLS, parallel_tool_calls=False)


async def resolve_issue(state: AgentState) -> dict:
    system = PROMPT.format(
        employee_id=state["employee_id"],
        category=state["category"],
        priority=state["priority"],
        team=state["team"],
        airport=state["airport"],
        knowledge="\n\n".join(f"[{k['section']} · {k['source']}]\n{k['text']}" for k in state.get("knowledge", [])),
    )
    reply = await agent_llm.ainvoke([SystemMessage(system), *state["messages"]])
    return {"messages": [reply]}
