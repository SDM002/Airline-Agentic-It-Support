"""Index of an employee's chats. The messages themselves live in the LangGraph checkpointer."""

from app.db.mongo import conversations, now, out


async def save(thread_id: str, employee_id: str, first_message: str):
    await conversations.update_one(
        {"_id": thread_id},
        {"$set": {"updated_at": now()}, "$setOnInsert": {"employee_id": employee_id, "title": first_message[:80], "created_at": now()}},
        upsert=True,
    )


async def get(thread_id: str) -> dict | None:
    return out(await conversations.find_one({"_id": thread_id}))


async def list_for(employee_id: str) -> list[dict]:
    return [out(c) async for c in conversations.find({"employee_id": employee_id}).sort("updated_at", -1)]
