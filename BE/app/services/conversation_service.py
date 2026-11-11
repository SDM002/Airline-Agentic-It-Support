"""Chat list per employee; the messages themselves live in the LangGraph checkpointer."""

from app.config.settings import settings
from app.db.mongo import conversations, now, out


# Create the chat entry on the first message (title = start of that message), then update its time
async def save(thread_id: str, employee_id: str, first_message: str):
    await conversations.update_one(
        {"_id": thread_id},
        {
            "$set": {"updated_at": now()},
            "$setOnInsert": {"employee_id": employee_id, "title": first_message[: settings.CHAT_TITLE_MAX_CHARS], "created_at": now()},
        },
        upsert=True,
    )


# One chat entry
async def get(thread_id: str) -> dict | None:
    return out(await conversations.find_one({"_id": thread_id}))


# An employee's chats, newest first
async def list_for(employee_id: str) -> list[dict]:
    return [out(c) async for c in conversations.find({"employee_id": employee_id}).sort("updated_at", -1)]
