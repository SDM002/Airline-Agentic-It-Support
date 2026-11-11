"""search_knowledge node: RAG step that always runs before the agent uses any MongoDB tool.

Searches the SOPs and policies in Pinecone for the employee's issue and stores the best matches in the state,
so resolve_issue answers from the airline's own documents.
"""

from langchain.messages import HumanMessage

from app.agent.state import AgentState
from app.services import knowledge_service


async def search_knowledge(state: AgentState) -> dict:
    issue = next(m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage))
    return {"knowledge": await knowledge_service.search(issue, state["category"])}
