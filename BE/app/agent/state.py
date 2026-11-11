"""The shared state every graph node reads from and writes to."""

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    # messages: list  -> inherited; new messages are appended, not replaced

    # Who is chatting (set by the API, read by the tools)
    employee_id: str

    # Filled by the classify_issue node
    category: str
    priority: str
    team: str
    airport: str
    reason: str

    # Filled by the search_knowledge node (RAG): best matching SOP / policy sections
    knowledge: list[dict]

    # Filled by the guardrails on every message: was it blocked, and which rules fired
    blocked: bool
    guardrails: list[str]
