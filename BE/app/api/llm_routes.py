"""LLM endpoint for IT support: send a prompt straight to the Groq model to check it is working."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import require_roles
from app.config.settings import settings
from app.core.llm_client import llm

router = APIRouter(prefix="/llm", tags=["llm"], dependencies=[Depends(require_roles("it_support"))])


# Request body: the prompt to send
class AskRequest(BaseModel):
    prompt: str


# Ask the LLM a question and return its answer
@router.post("/ask")
async def ask(body: AskRequest):

    try:
        response = await llm.ainvoke(body.prompt)

        return {
            "model": settings.GROQ_MODEL,
            "answer": response.content
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="LLM service unavailable. Please check the Groq API key."
        )
