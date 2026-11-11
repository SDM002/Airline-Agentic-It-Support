from fastapi import APIRouter, Depends

from app.api.deps import require_roles
from app.core.domain import Category
from app.services import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"], dependencies=[Depends(require_roles("it_support"))])


@router.get("/search")
async def search(q: str, category: Category | None = None):
    return await knowledge_service.search(q, category)
