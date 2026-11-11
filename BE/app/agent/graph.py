"""Agent workflow: input_guard -> classify_issue -> search_knowledge (RAG) -> resolve_issue <-> tools -> output_guard."""

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


# Blocked -> END, follow-up -> resolve_issue, first message -> classify_issue
def after_input_guard(state: AgentState) -> str:
    """Choose the next node after the input guardrail."""
    if state["blocked"]:
        return END
    return "resolve_issue" if state.get("category") else "classify_issue"


# Graph over the shared AgentState
builder = StateGraph(AgentState)

# Nodes
builder.add_node("input_guard", input_guard)
builder.add_node("classify_issue", classify_issue)
builder.add_node("search_knowledge", search_knowledge)
# Retry when Groq rejects a malformed tool call
builder.add_node(
    "resolve_issue",
    resolve_issue,
    retry_policy=RetryPolicy(max_attempts=settings.AGENT_RETRY_ATTEMPTS, retry_on=BadRequestError),
)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_node("output_guard", output_guard)

# Edges
builder.add_edge(START, "input_guard")
builder.add_conditional_edges("input_guard", after_input_guard, ["classify_issue", "resolve_issue", END])
builder.add_edge("classify_issue", "search_knowledge")
builder.add_edge("search_knowledge", "resolve_issue")
# Tool call -> tools, final reply -> output_guard
builder.add_conditional_edges("resolve_issue", tools_condition, {"tools": "tools", END: "output_guard"})
builder.add_edge("tools", "resolve_issue")
builder.add_edge("output_guard", END)

# Chat memory and paused approvals saved in MongoDB
checkpointer = MongoDBSaver(sync_client, db_name=settings.MONGODB_DB)

graph = builder.compile(checkpointer=checkpointer)
