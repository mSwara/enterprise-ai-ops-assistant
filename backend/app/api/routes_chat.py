import uuid
from fastapi import APIRouter, HTTPException
from app.graph.graph_builder import compiled_graph
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Sends a message into the multi-agent graph. If thread_id is omitted, a
    new conversation is started and a fresh thread_id is generated and
    returned — the caller should reuse that thread_id for follow-up
    messages in the same conversation (this is what gives Phase 10's
    persistent memory its continuity across HTTP requests).
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = compiled_graph.invoke(
            {
                "messages": [{"role": "user", "content": request.message}],
                "next_agent": None,
                "findings": {},
                "validated": None,
                "requires_approval": None,
                "approved": None,
                "retry_count": 0,
                "critic_feedback": None,
                "latest_attempt_messages": None,
            },
            config=config,
        )
    except Exception as e:
        # Anything unexpected reaching this point is a genuine server
        # error (agent-level and tool-level errors are already handled
        # gracefully inside the graph itself, per Phase 9/11's fixes) —
        # return a clean 500 instead of leaking a raw traceback to the client.
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")

    if "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        return ChatResponse(
            thread_id=thread_id,
            reply="This request requires human approval before proceeding.",
            paused=True,
            approval_payload=payload,
            routed_to=result.get("next_agent"),
        )

    return ChatResponse(
        thread_id=thread_id,
        reply=result["messages"][-1].content,
        paused=False,
        routed_to=result.get("next_agent"),
        validated=result.get("validated"),
        retry_count=result.get("retry_count"),
    )