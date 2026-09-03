from typing import Annotated, Optional, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


def merge_findings(existing: dict, update: dict) -> dict:
    """
    Reducer for `findings`. Merges concurrent writes (e.g. from parallel
    customer_context/policy_context Send branches) instead of colliding.
    """
    if existing is None:
        existing = {}
    if update is None:
        return existing
    return {**existing, **update}


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: Optional[str]
    findings: Annotated[dict[str, Any], merge_findings]
    validated: Optional[bool]
    requires_approval: Optional[bool]
    approved: Optional[bool]
    retry_count: Optional[int]
    critic_feedback: Optional[str]
    # Deliberately NOT wrapped in a reducer — must be fully OVERWRITTEN on
    # every agent attempt (never accumulated), so the Critic always sees
    # exactly one attempt's messages, never a mix of old and new.
    latest_attempt_messages: Optional[list]