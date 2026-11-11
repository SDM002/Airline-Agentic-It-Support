"""MongoDB connection, collections and small helpers shared by all services."""

from datetime import datetime, timezone

from pymongo import AsyncMongoClient, MongoClient, ReturnDocument

from app.config.settings import settings

client = AsyncMongoClient(settings.MONGODB_URI.get_secret_value(), tz_aware=True)
db = client[settings.MONGODB_DB]

# The LangGraph checkpointer needs a sync client
sync_client = MongoClient(settings.MONGODB_URI.get_secret_value(), tz_aware=True)

users = db["users"]
tickets = db["tickets"]
comments = db["comments"]
approvals = db["approvals"]
audit_logs = db["audit_logs"]
counters = db["counters"]
conversations = db["conversations"]


def now() -> datetime:
    return datetime.now(timezone.utc)


async def next_id(name: str, prefix: str) -> str:
    counter = await counters.find_one_and_update(
        {"_id": name}, {"$inc": {"seq": 1}}, upsert=True, return_document=ReturnDocument.AFTER
    )
    return f"{prefix}-{counter['seq']}"


def out(doc: dict | None) -> dict | None:
    """Renames Mongo's _id to id for API responses."""
    if doc is None:
        return None
    doc = dict(doc)
    doc["id"] = doc.pop("_id")
    return doc


async def ping() -> bool:
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
