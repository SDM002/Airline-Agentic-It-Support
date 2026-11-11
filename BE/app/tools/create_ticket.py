"""Tool: create a ticket for the employee in this chat (requester and chat ID come from the state, not the LLM)."""

from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

from app.core.domain import Category, Priority, Team
from app.services import employee_service, ticket_service


# Create the ticket from the chat's messages and classified airport
@tool
async def create_ticket(summary: str, category: Category, priority: Priority, team: Team, runtime: ToolRuntime) -> dict:
    """Create a support ticket for the employee in this chat. Returns the new ticket ID."""
    employee = await employee_service.get_employee(runtime.state["employee_id"])
    description = "\n".join(m.content for m in runtime.state["messages"] if isinstance(m, HumanMessage))
    ticket = await ticket_service.create_ticket(
        title=summary,
        description=description,
        category=category,
        priority=priority,
        team=team,
        airport=runtime.state.get("airport", "UNKNOWN"),
        requester=employee,
        actor="agent",
        thread_id=runtime.config["configurable"]["thread_id"],
    )
    return {"ticket_id": ticket["id"], "status": ticket["status"], "team": ticket["team"], "sla_hours": ticket["sla_hours"]}
