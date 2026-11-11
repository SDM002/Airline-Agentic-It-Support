"""Tool: find similar tickets, used to detect several reports of the same problem at one airport."""

from langchain.tools import tool

from app.services import ticket_service


# Similar tickets with status and creation time
@tool
async def find_similar_tickets(description: str, airport: str | None = None) -> dict:
    """Find past and open tickets that look like this issue, with status and timestamps.
    Pass the airport code to look for several reports of the same problem at one airport."""
    results = await ticket_service.find_similar_tickets(description, airport)
    tickets = [
        {
            "id": t["id"],
            "title": t["title"],
            "status": t["status"],
            "airport": t["airport"],
            "team": t["team"],
            "priority": t["priority"],
            "created_at": t["created_at"].isoformat(),
        }
        for t in results
    ]
    return {"count": len(tickets), "tickets": tickets}
