from langchain.tools import tool

from app.services import ticket_service


@tool
async def find_similar_tickets(description: str, airport: str | None = None) -> list[dict]:
    """Find past and open tickets that look like this issue, with status and timestamps.
    Pass the airport code to look for several reports of the same problem at one airport."""
    results = await ticket_service.find_similar_tickets(description, airport)
    keep = ("id", "title", "status", "airport", "team", "priority", "created_at")
    return [{k: t[k] for k in keep} for t in results]
