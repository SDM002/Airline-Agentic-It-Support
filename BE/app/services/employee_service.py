"""Reads employee records. Used by the API and by the get_employee_profile tool. Never returns password hashes."""

from app.db.mongo import out, users

HIDDEN = {"password_hash": 0}


async def get_employee(employee_id: str) -> dict | None:
    return out(await users.find_one({"_id": employee_id}, HIDDEN))


async def list_employees() -> list[dict]:
    return [out(u) async for u in users.find({}, HIDDEN).sort("_id")]
