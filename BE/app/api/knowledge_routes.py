from fastapi import APIRouter

from app.core.domain import Category
from app.services import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/search")
async def search(q: str, category: Category | None = None):
    return await knowledge_service.search(q, category)
