"""SkyDesk AI backend entrypoint. Creates the FastAPI app and registers the routers."""

from fastapi import FastAPI

from app.api import agent_routes, approval_routes, employee_routes, knowledge_routes, llm_routes, ticket_routes
from app.config.settings import settings
from app.db import mongo

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.include_router(llm_routes.router)
app.include_router(agent_routes.router)
app.include_router(ticket_routes.router)
app.include_router(approval_routes.router)
app.include_router(employee_routes.router)
app.include_router(knowledge_routes.router)


@app.get("/health")
async def health():
    return {"status": "ok", "mongodb": "connected" if await mongo.ping() else "down"}
