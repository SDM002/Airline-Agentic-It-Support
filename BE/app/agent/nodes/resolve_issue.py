"""resolve_issue node: the agent's decision step. The LLM gets the classification and RAG results in its prompt,
then either calls one tool or writes the final reply to the employee.
"""

from pathlib import Path

from langchain.messages import SystemMessage

from app.agent.state import AgentState
from app.config.settings import settings
from app.core.llm_client import llm
from app.tools import TOOLS

PROMPT = (Path(__file__).parents[2] / "prompts" / "resolve_issue.txt").read_text()

# LLM that can call the agent's tools, one at a time
agent_llm = llm.bind_tools(TOOLS, parallel_tool_calls=False)


# Fill the system prompt from the state, then let the LLM choose the next step
async def resolve_issue(state: AgentState) -> dict:
    system = PROMPT.format(
        app_name=settings.APP_NAME,
        airline_name=settings.AIRLINE_NAME,
        employee_id=state["employee_id"],
        category=state["category"],
        priority=state["priority"],
        team=state["team"],
        airport=state["airport"],
        knowledge="\n\n".join(f"[{k['section']} · {k['source']}]\n{k['text']}" for k in state.get("knowledge", [])),
    )
    reply = await agent_llm.ainvoke([SystemMessage(system), *state["messages"]])
    return {"messages": [reply]}
