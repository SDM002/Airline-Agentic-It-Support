"""Employee records for the API and the get_employee_profile tool; password hashes are never returned."""

from app.db.mongo import out, users

# Projection that hides the password hash
HIDDEN = {"password_hash": 0}


# One employee by ID
async def get_employee(employee_id: str) -> dict | None:
    return out(await users.find_one({"_id": employee_id}, HIDDEN))


# All employees, sorted by ID
async def list_employees() -> list[dict]:
    return [out(u) async for u in users.find({}, HIDDEN).sort("_id")]
