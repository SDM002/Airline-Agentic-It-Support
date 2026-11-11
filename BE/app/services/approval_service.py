"""Approval workflow for sensitive actions (access requests). Only managers or IT support may decide."""

from app.db.mongo import approvals, next_id, now, out
from app.services import employee_service, ticket_service

APPROVER_ROLES = {"manager", "it_support"}


async def request_approval(ticket_id: str, action: str, reason: str, thread_id: str) -> dict:
    # Idempotent: LangGraph re-runs the tool on resume, so reuse the existing approval
    existing = await approvals.find_one({"ticket_id": ticket_id, "action": action})
    if existing:
        return out(existing)

    approval = {
        "_id": await next_id("approval", "APR"),
        "ticket_id": ticket_id,
        "action": action,
        "reason": reason,
        "status": "pending",
        "thread_id": thread_id,
        "decided_by": None,
        "created_at": now(),
    }
    await approvals.insert_one(approval)
    await ticket_service.update_ticket(ticket_id, "agent", {"status": "awaiting-approval"})
    await ticket_service.log(ticket_id, "agent", f"Approval requested: {action}")
    return out(approval)


async def list_approvals(status: str | None) -> list[dict]:
    query = {"status": status} if status else {}
    return [out(a) async for a in approvals.find(query).sort("created_at", -1)]


async def get_approval(approval_id: str) -> dict | None:
    return out(await approvals.find_one({"_id": approval_id}))


async def decide(approval_id: str, approve: bool, decided_by: str, comment: str | None) -> dict:
    approval = await approvals.find_one({"_id": approval_id})
    if approval is None:
        raise LookupError("Approval not found")
    if approval["status"] != "pending":
        raise ValueError(f"Approval already {approval['status']}")

    approver = await employee_service.get_employee(decided_by)
    if approver is None or approver["role"] not in APPROVER_ROLES:
        raise PermissionError("Only a manager or IT support can approve")

    status = "approved" if approve else "rejected"
    await approvals.update_one(
        {"_id": approval_id},
        {"$set": {"status": status, "decided_by": approver["name"], "comment": comment, "decided_at": now()}},
    )

    ticket_id = approval["ticket_id"]
    if approve:
        note = f"Approved by {approver['name']}. Access provisioned by IAM (simulated)."
        await ticket_service.update_ticket(ticket_id, approver["name"], {"status": "resolved", "assignee": "L2"}, note)
    else:
        note = f"Rejected by {approver['name']}." + (f" Reason: {comment}" if comment else "")
        await ticket_service.update_ticket(ticket_id, approver["name"], {"status": "closed"}, note)

    return out(await approvals.find_one({"_id": approval_id}))
