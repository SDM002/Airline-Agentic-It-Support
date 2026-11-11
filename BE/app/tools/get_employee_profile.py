"""Tool: read an employee's profile (department, location, manager) from MongoDB."""

from langchain.tools import tool

from app.services import employee_service


# Employee profile, or an error if not found
@tool
async def get_employee_profile(employee_id: str) -> dict:
    """Get an employee's name, title, department, airport/location, role and manager ID."""
    employee = await employee_service.get_employee(employee_id)
    return employee or {"error": f"Employee {employee_id} not found"}
