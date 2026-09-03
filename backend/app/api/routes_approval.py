from fastapi import APIRouter, HTTPException

from app.graph.approvals import (
    list_pending_approvals,
    resume_approval,
    ThreadNotPendingError,
)
from app.schemas.approval import (
    ApprovalListResponse,
    PendingApproval,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
)

router = APIRouter()


@router.get("/approvals", response_model=ApprovalListResponse)
def get_pending_approvals():
    """
    Lists all threads currently paused, awaiting human approval.
    Backed directly by list_pending_approvals().
    """
    pending = list_pending_approvals()

    return ApprovalListResponse(
        count=len(pending),
        pending=[
            PendingApproval(
                thread_id=p["thread_id"],
                request=p["payload"].get("request"),
                reason=p["payload"].get("reason"),
                recommendation=p["payload"].get("recommendation"),
            )
            for p in pending
        ],
    )


@router.post(
    "/approvals/{thread_id}/resume",
    response_model=ApprovalDecisionResponse,
)
def resume_thread(
    thread_id: str,
    decision: ApprovalDecisionRequest,
):
    """
    Resumes a paused thread with a human approval/rejection decision.
    """
    try:
        result = resume_approval(
            thread_id=thread_id,
            approved=decision.approved,
            note=decision.note,
        )

    except ThreadNotPendingError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Could not resume thread '{thread_id}': {str(e)}",
        )

    return ApprovalDecisionResponse(
        thread_id=thread_id,
        approved=result.get("approved", decision.approved),
        reply=result["messages"][-1].content,
    )

