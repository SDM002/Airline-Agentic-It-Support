"""SkyDesk AI backend entrypoint. Creates the FastAPI app and registers the routers."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from groq import RateLimitError

from app.api import (
    agent_routes,
    approval_routes,
    auth_routes,
    employee_routes,
    knowledge_routes,
    llm_routes,
    meta_routes,
    ticket_routes,
)
from app.config.settings import settings
from app.db import mongo

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Lets the Next.js frontend call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(agent_routes.router)
app.include_router(ticket_routes.router)
app.include_router(approval_routes.router)
app.include_router(employee_routes.router)
app.include_router(knowledge_routes.router)
app.include_router(llm_routes.router)
app.include_router(meta_routes.router)


@app.exception_handler(RateLimitError)
async def llm_rate_limited(request, exc):
    return JSONResponse(status_code=503, content={"detail": agent_routes.LLM_BUSY})


@app.get("/health")
async def health():
    return {"status": "ok", "mongodb": "connected" if await mongo.ping() else "down"}
