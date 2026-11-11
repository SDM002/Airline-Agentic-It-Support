"""Builds the agent workflow.

START -> input_guard -> classify_issue -> search_knowledge (RAG) -> resolve_issue <-> tools -> output_guard -> END
              |          (first message of a chat only)                ^
              |                                follow-up messages start here
              +--> END when the input guardrail blocks the message
"""

from groq import BadRequestError
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import RetryPolicy

from app.agent.nodes.classify_issue import classify_issue
from app.agent.nodes.resolve_issue import resolve_issue
from app.agent.nodes.search_knowledge import search_knowledge
from app.agent.state import AgentState
from app.config.settings import settings
from app.db.mongo import sync_client
from app.guardrails.input_guard import input_guard
from app.guardrails.output_guard import output_guard
from app.tools import TOOLS


def after_input_guard(state: AgentState) -> str:
    if state["blocked"]:
        return END
    # Classify and search the knowledge base once per chat; follow-up messages go straight to resolve_issue
    return "resolve_issue" if state.get("category") else "classify_issue"


builder = StateGraph(AgentState)

builder.add_node("input_guard", input_guard)
builder.add_node("classify_issue", classify_issue)
builder.add_node("search_knowledge", search_knowledge)
# Groq returns 400 when the model writes a broken tool call; asking again usually fixes it
builder.add_node(
    "resolve_issue",
    resolve_issue,
    retry_policy=RetryPolicy(max_attempts=settings.AGENT_RETRY_ATTEMPTS, retry_on=BadRequestError),
)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_node("output_guard", output_guard)

builder.add_edge(START, "input_guard")
builder.add_conditional_edges("input_guard", after_input_guard, ["classify_issue", "resolve_issue", END])
builder.add_edge("classify_issue", "search_knowledge")
builder.add_edge("search_knowledge", "resolve_issue")
# No tool call means the agent wrote its final reply: check it before the employee sees it
builder.add_conditional_edges("resolve_issue", tools_condition, {"tools": "tools", END: "output_guard"})
builder.add_edge("tools", "resolve_issue")
builder.add_edge("output_guard", END)

# Chat memory and paused approvals are stored in MongoDB, so they survive a server restart
checkpointer = MongoDBSaver(sync_client, db_name=settings.MONGODB_DB)

graph = builder.compile(checkpointer=checkpointer)
