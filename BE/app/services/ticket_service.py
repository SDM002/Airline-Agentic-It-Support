"""Ticket business logic. The API routes (humans) and the agent tools (LLM) both call these functions."""

from pymongo import ReturnDocument

from app.config.settings import settings
from app.db.mongo import audit_logs, comments, next_id, now, out, tickets


async def log(ticket_id: str, actor: str, event: str):
    await audit_logs.insert_one({"ticket_id": ticket_id, "actor": actor, "event": event, "at": now()})


async def add_comment(ticket_id: str, author: str, text: str):
    await comments.insert_one({"ticket_id": ticket_id, "author": author, "text": text, "created_at": now()})


async def create_ticket(*, title, description, category, priority, team, airport, requester, actor, thread_id=None) -> dict:
    ticket = {
        "_id": await next_id("ticket", "SKY"),
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "team": team,
        "status": "open",
        "assignee": None,
        "airport": airport,
        "requester_id": requester["id"],
        "requester_name": requester["name"],
        "source": "chat",
        "thread_id": thread_id,
        "sla_hours": settings.SLA_HOURS[priority],
        "created_at": now(),
        "updated_at": now(),
    }
    await tickets.insert_one(ticket)
    await log(ticket["_id"], actor, "Ticket created via chat")
    return out(ticket)


async def get_ticket(ticket_id: str) -> dict | None:
    return out(await tickets.find_one({"_id": ticket_id}))


async def get_ticket_detail(ticket_id: str) -> dict | None:
    ticket = await get_ticket(ticket_id)
    if ticket:
        ticket["comments"] = await comments.find({"ticket_id": ticket_id}, {"_id": 0}).sort("created_at").to_list()
        ticket["audit"] = await audit_logs.find({"ticket_id": ticket_id}, {"_id": 0}).sort("at").to_list()
    return ticket


async def latest_comment(ticket_id: str) -> str | None:
    comment = await comments.find_one({"ticket_id": ticket_id}, sort=[("created_at", -1)])
    return comment["text"] if comment else None


async def list_tickets(filters: dict) -> list[dict]:
    query = {k: v for k, v in filters.items() if v is not None}
    return [out(t) async for t in tickets.find(query).sort("created_at", -1)]


async def update_ticket(ticket_id: str, actor: str, changes: dict, comment: str | None = None) -> dict | None:
    changes = {k: v for k, v in changes.items() if v is not None}
    if changes:
        ticket = await tickets.find_one_and_update(
            {"_id": ticket_id}, {"$set": {**changes, "updated_at": now()}}, return_document=ReturnDocument.AFTER
        )
    else:
        ticket = await tickets.find_one({"_id": ticket_id})
    if ticket is None:
        return None
    for field, value in changes.items():
        await log(ticket_id, actor, f"{field} -> {value}")
    if comment:
        await add_comment(ticket_id, actor, comment)
    return out(ticket)


async def find_similar_tickets(description: str, airport: str | None = None) -> list[dict]:
    query = {"$text": {"$search": description}}
    if airport and airport != "UNKNOWN":
        query["airport"] = airport
    cursor = (
        tickets.find(query, {"score": {"$meta": "textScore"}})
        .sort([("score", {"$meta": "textScore"})])
        .limit(settings.SIMILAR_TICKETS_LIMIT)
    )
    return [out(t) async for t in cursor]
