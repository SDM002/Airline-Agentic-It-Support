from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import require_roles
from app.services import employee_service

router = APIRouter(prefix="/employees", tags=["employees"], dependencies=[Depends(require_roles("manager", "it_support"))])


@router.get("")
async def list_employees():
    return await employee_service.list_employees()


@router.get("/{employee_id}")
async def get_employee(employee_id: str):
    employee = await employee_service.get_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee
