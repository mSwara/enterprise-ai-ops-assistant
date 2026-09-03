from typing import Literal
from pydantic import BaseModel, Field
from app.llm.client import get_llm


class RoutingDecision(BaseModel):
    agent: Literal[
        "customer_agent", "sql_agent", "knowledge_agent", "action_agent", "multi_context"
    ] = Field(
        description=(
            "Which path should handle this request. "
            "customer_agent: customer/order/payment/ticket lookups for a specific customer. "
            "sql_agent: analytical questions requiring counting, filtering, or aggregating across many records. "
            "knowledge_agent: questions about company policies, FAQs, or documentation ONLY, with NO specific customer/order involved. "
            "action_agent: requests to directly create a ticket or send an email — NOT refund approval questions. "
            "multi_context: REQUIRED whenever the request mentions BOTH a specific customer/order AND asks "
            "whether to approve/process a refund, discount, or similar financial decision. This is true even "
            "if the word 'approve' appears — approval QUESTIONS (should I approve this?) are multi_context, "
            "NOT action_agent. action_agent is only for requests to directly DO something routine (create a "
            "ticket, send an email) with no financial judgment call involved. "
            "Example that MUST be multi_context: 'Customer 3 wants a refund of 8000 for order 238. Should I "
            "approve it?' — this needs customer 3's order 238 details AND the refund policy threshold."
        )
    )

    reason: str = Field(description="Brief reason for this routing choice.")
    is_sensitive: bool = Field(
        description=(
            "True if this request involves a sensitive action requiring human "
            "approval before execution — e.g. refunds, cancellations, or any "
            "action with financial/customer impact beyond routine lookups."
        )
    )



def route_request(user_message: str, recent_context: str = "") -> RoutingDecision:
    llm = get_llm()
    structured_llm = llm.with_structured_output(RoutingDecision)

    context_block = (
        f"RECENT CONVERSATION CONTEXT (for reference only, to resolve pronouns "
        f"or vague follow-ups like 'that' or 'them'):\n{recent_context}\n\n"
        if recent_context else ""
    )

    prompt = (
        "You are the Supervisor of a multi-agent enterprise operations system. "
        f"{context_block}"
        "Given the user's CURRENT request below, decide which path should "
        "handle it, and whether it involves a sensitive action requiring "
        "human approval before execution. If the current request references "
        "something from the recent context (e.g. 'that', 'them', 'it'), route "
        "based on what it actually refers to, not the literal words alone.\n\n"
        f"CURRENT REQUEST: {user_message}"
    )

    try:
        return structured_llm.invoke(prompt)
    except Exception as e:
        try:
            return structured_llm.invoke(
                prompt + "\n\nIMPORTANT: You MUST respond using the structured "
                "tool call format. Do not respond with plain text."
            )
        except Exception:
            return RoutingDecision(
                agent="knowledge_agent",
                reason=f"Routing failed after retry ({str(e)[:100]}); defaulted to knowledge_agent as a safe fallback.",
                is_sensitive=False,
            )