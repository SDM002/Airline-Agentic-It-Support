"""Builds the agent workflow.

START -> classify_issue (first message only) -> resolve_issue <-> tools -> END
"""

from groq import BadRequestError
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import RetryPolicy

from app.agent.nodes.classify_issue import classify_issue
from app.agent.nodes.resolve_issue import resolve_issue
from app.agent.state import AgentState
from app.config.settings import settings
from app.db.mongo import sync_client
from app.tools import TOOLS


def start_route(state: AgentState) -> str:
    # Classify only once per chat; follow-up messages go straight to resolve_issue
    return "resolve_issue" if state.get("category") else "classify_issue"


builder = StateGraph(AgentState)

builder.add_node("classify_issue", classify_issue)
# Groq returns 400 when the model writes a broken tool call; asking again usually fixes it
builder.add_node(
    "resolve_issue",
    resolve_issue,
    retry_policy=RetryPolicy(max_attempts=settings.AGENT_RETRY_ATTEMPTS, retry_on=BadRequestError),
)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_conditional_edges(START, start_route, ["classify_issue", "resolve_issue"])
builder.add_edge("classify_issue", "resolve_issue")
builder.add_conditional_edges("resolve_issue", tools_condition, ["tools", END])
builder.add_edge("tools", "resolve_issue")

# Chat memory and paused approvals are stored in MongoDB, so they survive a server restart
checkpointer = MongoDBSaver(sync_client, db_name=settings.MONGODB_DB)

graph = builder.compile(checkpointer=checkpointer)
