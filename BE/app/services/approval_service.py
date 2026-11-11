"""Access request approvals: the requester's line manager or the ACCESS_APPROVER_TEAM decides, never the requester."""

from app.config.settings import settings
from app.db.mongo import approvals, next_id, now, out, tickets, users
from app.services import employee_service, ticket_service


# Create a pending approval and set the ticket to awaiting-approval (reuses an existing one on resume)
async def request_approval(ticket_id: str, action: str, reason: str, thread_id: str) -> dict:
    existing = await approvals.find_one({"ticket_id": ticket_id, "action": action})
    if existing:
        return out(existing)

    approval = {
        "_id": await next_id("approval", settings.APPROVAL_ID_PREFIX),
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


# True if the approver is the requester's line manager or in ACCESS_APPROVER_TEAM, and not the requester
def can_decide(approver: dict, requester: dict) -> bool:
    if approver["id"] == requester["id"]:
        return False
    if approver["role"] == "it_support" and approver.get("team") == settings.ACCESS_APPROVER_TEAM:
        return True
    return approver["role"] == "manager" and requester.get("manager_id") == approver["id"]


# Approvals with their tickets, newest first; managers see only their team members' requests
async def list_approvals(user: dict, status: str | None) -> list[dict]:
    query = {"status": status} if status else {}
    if user["role"] == "manager":
        reports = await users.distinct("_id", {"manager_id": user["id"]})
        query["ticket_id"] = {"$in": await tickets.distinct("_id", {"requester_id": {"$in": reports}})}

    result = []
    async for approval in approvals.find(query).sort("created_at", -1):
        approval = out(approval)
        approval["ticket"] = await ticket_service.get_ticket(approval["ticket_id"])
        result.append(approval)
    return result


# Approve (ticket resolved) or reject (ticket closed) after checking who may decide
async def decide(approval_id: str, approve: bool, approver: dict, comment: str | None) -> dict:
    approval = await approvals.find_one({"_id": approval_id})
    if approval is None:
        raise LookupError("Approval not found")
    if approval["status"] != "pending":
        raise ValueError(f"Approval already {approval['status']}")

    ticket = await ticket_service.get_ticket(approval["ticket_id"])
    requester = await employee_service.get_employee(ticket["requester_id"])
    if not can_decide(approver, requester):
        raise PermissionError("Only the requester's line manager or IAM can decide this request")

    status = "approved" if approve else "rejected"
    await approvals.update_one(
        {"_id": approval_id},
        {"$set": {"status": status, "decided_by": approver["name"], "comment": comment, "decided_at": now()}},
    )

    if approve:
        note = f"Approved by {approver['name']}. Access provisioned by IAM (simulated)."
        await ticket_service.update_ticket(ticket["id"], approver["name"], {"status": "resolved", "assignee": "L2"}, note)
    else:
        note = f"Rejected by {approver['name']}." + (f" Reason: {comment}" if comment else "")
        await ticket_service.update_ticket(ticket["id"], approver["name"], {"status": "closed"}, note)

    return out(await approvals.find_one({"_id": approval_id}))
