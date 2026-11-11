"""Agent state: the shared data of one chat that every graph node reads and updates."""

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """Chat state saved per thread: messages (appended) plus the employee, classification, RAG results and guardrail flags (overwritten)."""

    # Who is chatting (set by the API from the login token, read by the tools)
    employee_id: str

    # Issue classification (set by classify_issue)
    category: str
    priority: str
    team: str
    airport: str
    reason: str

    # Best matching SOP / policy sections from Pinecone (set by search_knowledge)
    knowledge: list[dict]

    # Guardrail result for the latest message (set by input_guard and output_guard)
    blocked: bool
    guardrails: list[str]
