from langchain.tools import tool

from app.core.domain import Status
from app.services import ticket_service


@tool
async def update_ticket(ticket_id: str, status: Status, comment: str) -> dict:
    """Change a ticket's status and add a comment explaining why."""
    ticket = await ticket_service.update_ticket(ticket_id, "agent", {"status": status}, comment)
    return {"ticket_id": ticket_id, "status": ticket["status"]} if ticket else {"error": "Ticket not found"}
