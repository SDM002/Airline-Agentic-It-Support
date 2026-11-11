from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.domain import Level, Priority, Status, Team
from app.services import ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])


class TicketUpdate(BaseModel):
    actor: str
    status: Status | None = None
    priority: Priority | None = None
    team: Team | None = None
    assignee: Level | None = None
    comment: str | None = None


@router.get("")
async def list_tickets(status: Status | None = None, team: Team | None = None, requester_id: str | None = None):
    return await ticket_service.list_tickets({"status": status, "team": team, "requester_id": requester_id})


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str):
    ticket = await ticket_service.get_ticket_detail(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}")
async def update_ticket(ticket_id: str, body: TicketUpdate):
    changes = body.model_dump(exclude={"actor", "comment"})
    ticket = await ticket_service.update_ticket(ticket_id, body.actor, changes, body.comment)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
