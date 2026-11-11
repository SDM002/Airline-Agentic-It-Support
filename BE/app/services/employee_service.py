"""Reads employee records. Used by the API and by the get_employee_profile tool."""

from app.db.mongo import out, users


async def get_employee(employee_id: str) -> dict | None:
    return out(await users.find_one({"_id": employee_id}))


async def list_employees() -> list[dict]:
    return [out(u) async for u in users.find().sort("_id")]
