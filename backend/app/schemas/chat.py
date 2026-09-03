from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's message.")
    thread_id: Optional[str] = Field(
        None,
        description="Conversation thread ID. Omit to start a new conversation; a new ID will be generated and returned.",
    )


class ChatResponse(BaseModel):
    thread_id: str
    reply: str
    paused: bool = Field(description="True if this request requires human approval before proceeding.")
    approval_payload: Optional[dict] = Field(
        None, description="Present only when paused=True. Contains request, reason, and recommendation."
    )
    routed_to: Optional[str] = None
    validated: Optional[bool] = None
    retry_count: Optional[int] = None