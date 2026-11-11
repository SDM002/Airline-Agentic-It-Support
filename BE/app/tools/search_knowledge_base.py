from langchain.tools import tool

from app.core.domain import Category
from app.services import knowledge_service


@tool
async def search_knowledge_base(query: str, category: Category | None = None) -> list[dict]:
    """Search Saffron Air's IT troubleshooting SOPs and IT policies (priority, SLA, escalation, access approval).
    Returns the most relevant sections with their source. Use it before giving any troubleshooting steps."""
    return await knowledge_service.search(query, category)
