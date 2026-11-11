"""MongoDB Atlas connection, the collections, and small helpers (time, IDs, response format) shared by all services."""

from datetime import datetime, timezone

from pymongo import AsyncMongoClient, MongoClient, ReturnDocument

from app.config.settings import settings

# Async client for the API and services
client = AsyncMongoClient(settings.MONGODB_URI.get_secret_value(), tz_aware=True)
db = client[settings.MONGODB_DB]

# Sync client for the LangGraph checkpointer
sync_client = MongoClient(settings.MONGODB_URI.get_secret_value(), tz_aware=True)

# Collections
users = db["users"]
tickets = db["tickets"]
comments = db["comments"]
approvals = db["approvals"]
audit_logs = db["audit_logs"]
counters = db["counters"]
conversations = db["conversations"]


# Current time in UTC
def now() -> datetime:
    return datetime.now(timezone.utc)


# Next readable ID from an atomic counter, e.g. <prefix>-1061
async def next_id(name: str, prefix: str) -> str:
    counter = await counters.find_one_and_update(
        {"_id": name}, {"$inc": {"seq": 1}}, upsert=True, return_document=ReturnDocument.AFTER
    )
    return f"{prefix}-{counter['seq']}"


# Rename Mongo's _id to id for API responses
def out(doc: dict | None) -> dict | None:
    if doc is None:
        return None
    doc = dict(doc)
    doc["id"] = doc.pop("_id")
    return doc


# True if MongoDB answers (used by /health)
async def ping() -> bool:
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
