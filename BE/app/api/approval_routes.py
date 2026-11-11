from fastapi import APIRouter, HTTPException
from langgraph.types import Command
from pydantic import BaseModel

from app.agent.graph import graph
from app.services import approval_service

router = APIRouter(prefix="/approvals", tags=["approvals"])


class Decision(BaseModel):
    approve: bool
    decided_by: str
    comment: str | None = None


@router.get("")
async def list_approvals(status: str | None = "pending"):
    return await approval_service.list_approvals(status)


@router.post("/{approval_id}/decision")
async def decide(approval_id: str, body: Decision):

    try:
        approval = await approval_service.decide(approval_id, body.approve, body.decided_by, body.comment)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    # Approvals loaded as demo data have no paused chat to resume
    if not approval["thread_id"]:
        return {"approval": approval, "agent_reply": None}

    # Resume the paused agent conversation with the human decision
    config = {"configurable": {"thread_id": approval["thread_id"]}}
    decision = {"status": approval["status"], "decided_by": approval["decided_by"], "comment": body.comment}
    state = await graph.ainvoke(Command(resume=decision), config)

    return {"approval": approval, "agent_reply": state["messages"][-1].content}
