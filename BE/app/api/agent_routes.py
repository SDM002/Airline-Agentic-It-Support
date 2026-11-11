from uuid import uuid4

from fastapi import APIRouter, HTTPException
from langchain.messages import HumanMessage
from pydantic import BaseModel

from app.agent.graph import graph
from app.services import employee_service

router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    employee_id: str
    message: str
    thread_id: str | None = None


@router.post("/chat")
async def chat(body: ChatRequest):

    if await employee_service.get_employee(body.employee_id) is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    thread_id = body.thread_id or str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    state = await graph.ainvoke(
        {"messages": [HumanMessage(body.message)], "employee_id": body.employee_id}, config
    )

    interrupts = state.get("__interrupt__", [])
    reply = interrupts[0].value["message"] if interrupts else state["messages"][-1].content

    return {
        "thread_id": thread_id,
        "reply": reply,
        "category": state["category"],
        "priority": state["priority"],
        "team": state["team"],
        "airport": state["airport"],
        "awaiting_approval": [i.value for i in interrupts],
    }
