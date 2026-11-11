"""Knowledge base endpoint for IT support: test the RAG search (Pinecone vector search + rerank) directly."""

from fastapi import APIRouter, Depends

from app.api.deps import require_roles
from app.core.domain import Category
from app.services import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"], dependencies=[Depends(require_roles("it_support"))])


# Best matching SOP / policy sections for a query, optionally narrowed by category
@router.get("/search")
async def search(q: str, category: Category | None = None):
    return await knowledge_service.search(q, category)
