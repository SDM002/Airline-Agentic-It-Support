import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.sse import EventSourceResponse
from groq import RateLimitError
from langchain.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from app.agent.graph import graph
from app.api.deps import current_user
from app.guardrails import rules
from app.services import conversation_service

router = APIRouter(prefix="/agent", tags=["agent"])

LLM_BUSY = "The AI assistant is busy (LLM usage limit reached). Please try again later."

# Save chat memory only when a run ends, after the input guardrail has removed any password from the message
SAVE_AT_END = "exit"


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


async def own_conversation(thread_id: str, user: dict) -> dict:
    conversation = await conversation_service.get(thread_id)
    if conversation is None or conversation["employee_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


async def chat_thread(body: ChatRequest, user: dict = Depends(current_user)) -> str:
    """The chat to continue (must belong to this employee), or a new one."""
    if body.thread_id:
        await own_conversation(body.thread_id, user)
        return body.thread_id
    return str(uuid4())


@router.post("/chat")
async def chat(body: ChatRequest, thread_id: str = Depends(chat_thread), user: dict = Depends(current_user)):

    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.ainvoke({"messages": [HumanMessage(body.message)], "employee_id": user["id"]}, config, durability=SAVE_AT_END)
    await conversation_service.save(thread_id, user["id"], rules.safe_to_store(body.message))

    interrupts = state.get("__interrupt__", [])
    reply = interrupts[0].value["message"] if interrupts else state["messages"][-1].content

    return {
        "thread_id": thread_id,
        "reply": reply,
        "category": state.get("category"),
        "priority": state.get("priority"),
        "team": state.get("team"),
        "airport": state.get("airport"),
        "sources": [{"section": k["section"], "source": k["source"], "score": k["score"]} for k in state.get("knowledge", [])],
        "guardrails": state.get("guardrails", []),
        "awaiting_approval": [i.value for i in interrupts],
    }


def tool_output(content):
    try:
        return json.loads(content)
    except (TypeError, ValueError):
        return content


def step_events(node: str, update) -> list[dict]:
    """One graph node finished -> the events the chat screen shows for it."""
    if node == "input_guard":
        events = [{"type": "guardrail", "rule": rule} for rule in update["guardrails"]]
        if update["blocked"]:
            events.append({"type": "answer", "text": update["messages"][-1].content})
        return events
    if node == "output_guard":
        # The final reply is only sent after the output guardrail has checked it
        new_rules = [r for r in update["guardrails"] if r.startswith("output:")]
        return [{"type": "guardrail", "rule": rule} for rule in new_rules] + [{"type": "answer", "text": update["messages"][-1].content}]
    if node == "classify_issue":
        return [{"type": "classified", **update}]
    if node == "search_knowledge":
        return [{"type": "knowledge", "results": update["knowledge"]}]
    if node == "resolve_issue":
        message = update["messages"][-1]
        return [{"type": "tool_call", "tool": c["name"], "args": c["args"]} for c in message.tool_calls]
    if node == "tools":
        return [{"type": "tool_result", "tool": m.name, "result": tool_output(m.content)} for m in update["messages"]]
    if node == "__interrupt__":
        return [{"type": "approval", **i.value} for i in update]
    return []


@router.post("/chat/stream", response_class=EventSourceResponse)
async def chat_stream(body: ChatRequest, thread_id: str = Depends(chat_thread), user: dict = Depends(current_user)):
    """Same as /chat, but sends each agent step as it happens (server-sent events)."""

    await conversation_service.save(thread_id, user["id"], rules.safe_to_store(body.message))
    yield {"type": "start", "thread_id": thread_id}

    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"messages": [HumanMessage(body.message)], "employee_id": user["id"]}
    try:
        async for update in graph.astream(inputs, config, stream_mode="updates", durability=SAVE_AT_END):
            for node, data in update.items():
                for event in step_events(node, data):
                    yield event
    except RateLimitError:
        yield {"type": "error", "message": LLM_BUSY}

    yield {"type": "done", "thread_id": thread_id}


@router.get("/conversations")
async def list_conversations(user: dict = Depends(current_user)):
    return await conversation_service.list_for(user["id"])


@router.get("/conversations/{thread_id}")
async def get_conversation(thread_id: str, user: dict = Depends(current_user)):

    conversation = await own_conversation(thread_id, user)
    snapshot = await graph.aget_state({"configurable": {"thread_id": thread_id}})

    # Only the chat text: the employee's messages and the agent's replies (tool calls are hidden)
    messages = [
        {"from": "user" if isinstance(m, HumanMessage) else "agent", "text": m.content}
        for m in snapshot.values.get("messages", [])
        if isinstance(m, HumanMessage) or (isinstance(m, AIMessage) and m.content)
    ]

    return {**conversation, "messages": messages, "awaiting_approval": [i.value for i in snapshot.interrupts]}
