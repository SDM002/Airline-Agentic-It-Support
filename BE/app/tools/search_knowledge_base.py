"""Tool: search the SOPs and IT policies in Pinecone again (e.g. when the topic changes)."""

from langchain.tools import tool

from app.core.domain import Category
from app.services import knowledge_service


# RAG search, results wrapped in a dict
@tool
async def search_knowledge_base(query: str, category: Category | None = None) -> dict:
    """Search the airline's IT troubleshooting SOPs and IT policies (priority, SLA, escalation, access approval).
    Returns the most relevant sections with their source. Use it when the knowledge already given does not cover the problem."""
    return {"results": await knowledge_service.search(query, category)}
