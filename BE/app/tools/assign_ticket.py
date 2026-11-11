"""Tool: route a ticket to a support team at L1 or L2."""

from langchain.tools import tool

from app.core.domain import Level, Team
from app.services import ticket_service


# Set the ticket's team and level (L1 / L2)
@tool
async def assign_ticket(ticket_id: str, team: Team, level: Level) -> dict:
    """Route a ticket to a team at L1 (standard) or L2 (P1, outages, repeated failures)."""
    ticket = await ticket_service.update_ticket(ticket_id, "agent", {"team": team, "assignee": level})
    return {"ticket_id": ticket_id, "team": ticket["team"], "assignee": ticket["assignee"]} if ticket else {"error": "Ticket not found"}
