"""The fixed business values (teams, statuses, ...) so the frontend never keeps its own copy."""

from typing import get_args

from fastapi import APIRouter, Depends

from app.api.deps import current_user
from app.config.settings import settings
from app.core.domain import Category, Level, Priority, Status, Team

router = APIRouter(prefix="/meta", tags=["meta"], dependencies=[Depends(current_user)])


@router.get("")
async def meta():
    return {
        "airline": settings.AIRLINE_NAME,
        "categories": get_args(Category),
        "priorities": get_args(Priority),
        "teams": get_args(Team),
        "statuses": get_args(Status),
        "levels": get_args(Level),
    }
