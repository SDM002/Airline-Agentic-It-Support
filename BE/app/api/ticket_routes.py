from fastapi import APIRouter, Depends, HTTPException
from langchain.messages import AIMessage
from pydantic import BaseModel

from app.agent.graph import graph
from app.api.deps import current_user, require_roles
from app.core.domain import Level, Priority, Status, Team
from app.services import knowledge_service, ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])

it_only = require_roles("it_support")


class TicketUpdate(BaseModel):
    status: Status | None = None
    priority: Priority | None = None
    team: Team | None = None
    assignee: Level | None = None
    comment: str | None = None


@router.get("")
async def list_tickets(status: Status | None = None, team: Team | None = None, user: dict = Depends(it_only)):
    return await ticket_service.list_tickets({"status": status, "team": team})


@router.get("/mine")
async def my_tickets(user: dict = Depends(current_user)):
    return await ticket_service.list_tickets({"requester_id": user["id"]})


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str, user: dict = Depends(current_user)):

    ticket = await ticket_service.get_ticket_detail(ticket_id)
    if ticket is None or (user["role"] != "it_support" and ticket["requester_id"] != user["id"]):
        raise HTTPException(status_code=404, detail="Ticket not found")

    # What the agent would look at for this ticket
    query = f"{ticket['title']}. {ticket['description']}"
    ticket["similar"] = [t for t in await ticket_service.find_similar_tickets(query) if t["id"] != ticket_id]
    ticket["sops"] = await knowledge_service.search(query, ticket["category"])

    # What the agent did in the chat that created this ticket: the RAG step first, then each tool call
    ticket["trace"] = []
    if ticket.get("thread_id"):
        values = (await graph.aget_state({"configurable": {"thread_id": ticket["thread_id"]}})).values
        ticket["trace"] = [
            {"tool": "search_knowledge (RAG)", "args": {k["section"]: k["score"] for k in values.get("knowledge", [])}}
        ] + [
            {"tool": call["name"], "args": call["args"]}
            for m in values.get("messages", [])
            if isinstance(m, AIMessage)
            for call in m.tool_calls
        ]
    return ticket


@router.patch("/{ticket_id}")
async def update_ticket(ticket_id: str, body: TicketUpdate, user: dict = Depends(it_only)):
    changes = body.model_dump(exclude={"comment"})
    ticket = await ticket_service.update_ticket(ticket_id, user["name"], changes, body.comment)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
