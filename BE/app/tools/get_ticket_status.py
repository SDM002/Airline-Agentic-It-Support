"""Tool: status of one of the logged-in employee's own tickets."""

from langchain.tools import ToolRuntime, tool

from app.services import ticket_service


# Ticket status and latest comment, only for the employee's own tickets
@tool
async def get_ticket_status(ticket_id: str, runtime: ToolRuntime) -> dict:
    """Get a ticket's status, assignee and latest comment."""
    ticket = await ticket_service.get_ticket(ticket_id)
    if ticket is None or ticket["requester_id"] != runtime.state["employee_id"]:
        return {"error": f"No ticket {ticket_id} found for this employee"}
    return {
        "ticket_id": ticket["id"],
        "status": ticket["status"],
        "team": ticket["team"],
        "assignee": ticket["assignee"],
        "latest_comment": await ticket_service.latest_comment(ticket_id),
    }
