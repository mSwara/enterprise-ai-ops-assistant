from typing import Optional
from pydantic import BaseModel, Field


class PendingApproval(BaseModel):
    thread_id: str
    request: Optional[str] = None
    reason: Optional[str] = None
    recommendation: Optional[str] = None


class ApprovalListResponse(BaseModel):
    count: int
    pending: list[PendingApproval]


class ApprovalDecisionRequest(BaseModel):
    approved: bool
    note: str = Field("", description="Optional reviewer note explaining the decision.")


class ApprovalDecisionResponse(BaseModel):
    thread_id: str
    approved: bool
    reply: str