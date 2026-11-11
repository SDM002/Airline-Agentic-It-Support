from langchain.tools import ToolRuntime, tool
from langgraph.types import interrupt

from app.services import approval_service, ticket_service


@tool
async def request_approval(ticket_id: str, requested_access: str, reason: str, runtime: ToolRuntime) -> dict:
    """Ask a manager or IT support to approve a sensitive action (e.g. granting system access).
    The conversation pauses until a human decides. Never grant access without this."""
    if await ticket_service.get_ticket(ticket_id) is None:
        return {"error": f"Ticket {ticket_id} not found; create the ticket first"}

    approval = await approval_service.request_approval(
        ticket_id, requested_access, reason, runtime.config["configurable"]["thread_id"]
    )

    # Pauses the graph here. Resumes with the human decision from POST /approvals/{id}/decision
    decision = interrupt({
        "approval_id": approval["id"],
        "ticket_id": ticket_id,
        "requested_access": requested_access,
        "message": f"Ticket {ticket_id} is waiting for approval from your manager or IT support.",
    })

    return {"approval_id": approval["id"], "ticket_id": ticket_id, **decision}
