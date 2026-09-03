from langchain_core.messages import AIMessage
from app.graph.state import AgentState
from app.graph.critic import check_groundedness
from app.graph.tool_validation import extract_tool_errors

MAX_RETRIES = 2


def _get_original_question(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if msg.__class__.__name__ == "HumanMessage":
            content = getattr(msg, "content", None)
            if content:
                return content
    return ""



def _build_evidence(state: AgentState) -> str:
    """
    Evidence spans the ENTIRE persisted conversation. Each tool result is
    now tagged with the tool call that produced it (name + arguments) so
    the entity being referenced (e.g. customer_id=3) is explicit in the
    evidence text itself, rather than something the Critic has to infer
    by cross-referencing separate chunks. This removes the ambiguity that
    caused the Critic to occasionally over-fail correct, well-supported
    answers (see Step 11.4).
    """
    all_messages = state["messages"]

    # Build a lookup: tool_call_id -> "tool_name(args)" string, from every
    # AIMessage's tool_calls, so we can label each ToolMessage's result.
    call_labels = {}
    for msg in all_messages:
        if msg.__class__.__name__ == "AIMessage" and getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                args_str = ", ".join(f"{k}={v}" for k, v in tc.get("args", {}).items())
                call_labels[tc["id"]] = f"{tc['name']}({args_str})"

    tool_evidence = []
    for msg in all_messages:
        if msg.__class__.__name__ == "ToolMessage" and msg.content:
            tool_call_id = getattr(msg, "tool_call_id", None)
            label = call_labels.get(tool_call_id, "unknown_tool_call")
            tool_evidence.append(f"{label} -> {msg.content}")

    findings = state.get("findings", {})
    findings_evidence = [
        f"{k}: {v}" for k, v in findings.items() if k != "routing_reason"
    ]

    all_evidence = tool_evidence + findings_evidence

    if not all_evidence:
        return "No tool results or findings were recorded for this conversation."

    return "\n---\n".join(all_evidence)


def critic_node(state: AgentState) -> dict:
    # Tool-ERROR checking stays scoped to THIS attempt only.
    # An old failed tool call should not invalidate a later successful attempt.
    recent_messages = state.get("latest_attempt_messages") or []

    if not recent_messages:
        return {"validated": True, "critic_feedback": None}

    final_answer = recent_messages[-1].content
    original_question = _get_original_question(state)

    tool_errors = extract_tool_errors(recent_messages)

    if tool_errors:
        error_summary = "; ".join(
            f"{e['tool']}: {e['error']}"
            for e in tool_errors
        )

        return {
            "validated": False,
            "critic_feedback": f"Tool call(s) failed: {error_summary}",
            "retry_count": state.get("retry_count", 0) + 1,
        }

    # EVIDENCE for groundedness spans the entire persisted conversation.
    # This allows later follow-ups to reuse facts retrieved in earlier turns.
    evidence = _build_evidence(state)

    verdict = check_groundedness(
        answer=final_answer,
        evidence=evidence,
        original_question=original_question,
    )

    if verdict.verdict == "fail":
        return {
            "validated": False,
            "critic_feedback": verdict.issues,
            "retry_count": state.get("retry_count", 0) + 1,
        }

    return {
        "validated": True,
        "critic_feedback": None
    }


def route_after_critic(state: AgentState) -> str:
    if state.get("validated"):
        return "end"

    if state.get("retry_count", 0) >= MAX_RETRIES:
        return "give_up"

    return "retry"


def give_up_node(state: AgentState) -> dict:
    feedback = state.get(
        "critic_feedback",
        "the answer could not be verified"
    )

    return {
        "messages": [
            AIMessage(
                content=(
                    "I attempted to answer this but couldn't produce a fully "
                    f"grounded response after multiple attempts. Issue: {feedback}. "
                    "Please try rephrasing your question, or a team member can "
                    "look into this directly."
                )
            )
        ]
    }