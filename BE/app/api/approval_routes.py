"""Approval endpoints: managers and IAM see pending access requests and decide them.
A decision resumes the agent run that was paused by request_approval.
"""

from fastapi import APIRouter, Depends, HTTPException
from langgraph.types import Command
from pydantic import BaseModel

from app.agent.graph import graph
from app.api.agent_routes import SAVE_AT_END
from app.api.deps import require_roles
from app.services import approval_service

router = APIRouter(prefix="/approvals", tags=["approvals"])

# Only managers and IT support may open approvals
approver_only = require_roles("manager", "it_support")


# Request body: approve or reject, with an optional comment
class Decision(BaseModel):
    approve: bool
    comment: str | None = None


# Approvals the user may see (managers: their team only), pending by default
@router.get("")
async def list_approvals(status: str | None = "pending", user: dict = Depends(approver_only)):
    return await approval_service.list_approvals(user, status)


# Approve or reject a request, then resume the paused agent with the decision
@router.post("/{approval_id}/decision")
async def decide(approval_id: str, body: Decision, user: dict = Depends(approver_only)):

    try:
        approval = await approval_service.decide(approval_id, body.approve, user, body.comment)
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
    state = await graph.ainvoke(Command(resume=decision), config, durability=SAVE_AT_END)

    return {"approval": approval, "agent_reply": state["messages"][-1].content}
