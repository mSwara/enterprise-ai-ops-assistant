from langchain_core.messages import AIMessage, SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from langgraph.types import interrupt

from app.core.config import settings
from app.graph.state import AgentState
from app.graph.supervisor import route_request
from app.graph.nodes.customer_agent import customer_agent
from app.graph.nodes.sql_agent import sql_agent
from app.graph.nodes.knowledge_agent import knowledge_agent
from app.graph.nodes.action_agent import action_agent
from app.graph.nodes.critic_node import critic_node, route_after_critic, give_up_node
from app.llm.client import get_llm


def supervisor_node(state: AgentState) -> dict:
    messages = state["messages"]
    last_human_msg = messages[-1]
    content = getattr(last_human_msg, "content", None) or last_human_msg.get("content")

    # Build a short context summary from the last few messages (excluding
    # the current one) so the Supervisor can resolve vague follow-ups like
    # "that" or "them" — same problem Step 5.2/10.1 solved for AGENTS,
    # now solved for ROUTING too.
    prior_messages = messages[:-1][-6:]  # last 6 messages before the current one
    context_lines = []
    for msg in prior_messages:
        role = msg.__class__.__name__.replace("Message", "")
        text = getattr(msg, "content", None)
        if text:
            context_lines.append(f"{role}: {text[:200]}")
    recent_context = "\n".join(context_lines)

    decision = route_request(content, recent_context)

    return {
        "next_agent": decision.agent,
        "requires_approval": decision.is_sensitive,
        "findings": {"routing_reason": decision.reason},
    }


def make_agent_node(agent, name: str):
    """
    Standard agent node. On a normal (first) call, behaves exactly as in
    Phase 10 — no injected messages, `latest_attempt_messages` set fresh.

    On a RETRY (critic_feedback is set from a failed critic check), injects
    a SystemMessage carrying the Critic's specific feedback before invoking
    the agent, so the agent sees exactly what was wrong rather than being
    re-asked the same question blind.

    `latest_attempt_messages` is OVERWRITTEN (not appended) every call, so
    the Critic only ever evaluates the current attempt — never a stale
    previous attempt's tool errors or wrong answer.
    """
    def node(state: AgentState) -> dict:
        feedback = state.get("critic_feedback")
        input_messages = list(state["messages"])
        injected = []

        if feedback:
            correction = SystemMessage(
                content=(
                    "Your previous answer failed validation for this reason: "
                    f"{feedback} Re-answer the user's original question. Use "
                    "your tools again to get correct, current information — "
                    "do not repeat the same unsupported claim."
                )
            )
            injected = [correction]
            input_messages = input_messages + injected

        result = agent.invoke({"messages": input_messages})
        new_messages = result["messages"][len(input_messages):]

        return {
            "messages": injected + new_messages,
            "latest_attempt_messages": new_messages,
            "critic_feedback": None,  # consumed this attempt; cleared so it can't leak into an unrelated future retry
        }
    node.__name__ = name
    return node


def make_context_node(agent, findings_key: str):
    """Parallel-safe context-gathering node (multi_context path). Unchanged from Phase 10."""
    def node(state: AgentState) -> dict:
        result = agent.invoke({"messages": state["messages"]})
        answer = result["messages"][-1].content
        return {"findings": {findings_key: answer}}
    node.__name__ = f"context_{findings_key}"
    return node


customer_context_node = make_context_node(customer_agent, "customer_context")
policy_context_node = make_context_node(knowledge_agent, "policy_context")


def combine_results_node(state: AgentState) -> dict:
    findings = state.get("findings", {})
    customer_info = findings.get("customer_context", "No customer context retrieved.")
    policy_info = findings.get("policy_context", "No policy context retrieved.")

    original_request = state["messages"][0]
    original_text = getattr(original_request, "content", None) or original_request.get("content")

    llm = get_llm()
    synthesis_prompt = (
        "You are combining findings from two specialist agents to answer the "
        "user's original request. Base your answer ONLY on the information "
        "below — do not add facts not present here.\n\n"
        f"CUSTOMER/ORDER CONTEXT:\n{customer_info}\n\n"
        f"POLICY CONTEXT:\n{policy_info}\n\n"
        f"ORIGINAL USER REQUEST: {original_text}\n\n"
        "Write a clear, grounded recommendation combining both pieces of context."
    )
    synthesis = llm.invoke(synthesis_prompt)

    # Store the recommendation in findings so approval_required_node can
    # show it as part of what the human is approving.
    return {
        "messages": [AIMessage(content=synthesis.content)],
        "findings": {"recommendation": synthesis.content},
    }

  

def _get_original_question(state: AgentState) -> str:
    """
    Scans for the actual most recent HumanMessage, rather than assuming
    state["messages"][-1] is always the user's question — which breaks
    on the multi_context path, where combine_results_node appends an
    AIMessage before reaching this node.
    """
    for msg in reversed(state["messages"]):
        if msg.__class__.__name__ == "HumanMessage":
            content = getattr(msg, "content", None)
            if content:
                return content
    return ""


def approval_required_node(state: AgentState) -> dict:
    original_request = _get_original_question(state)
    recommendation = state.get("findings", {}).get("recommendation")

    human_decision = interrupt(
        {
            "type": "approval_required",
            "request": original_request,
            "reason": state.get("findings", {}).get("routing_reason", "Sensitive action detected."),
            "recommendation": recommendation,
        }
    )

    approved = human_decision.get("approved", False)
    approver_note = human_decision.get("note", "")

    if approved:
        content = (
            f"Approved by human reviewer. {approver_note}\n\n"
            "This action would now proceed to execution. "
            "(Actual execution wiring: Step 12.2.)"
        )
    else:
        content = (
            f"Request was NOT approved by human reviewer. {approver_note or 'No reason given.'}\n\n"
            "No action was taken."
        )

    return {
        "approved": approved,
        "messages": [AIMessage(content=content)],
    }



def route_after_supervisor(state: AgentState):
    """Unchanged from Phase 10."""
    if state["next_agent"] == "multi_context":
        return [
            Send("customer_context", state),
            Send("policy_context", state),
        ]
    if state.get("requires_approval"):
        return "approval_required"
    return state["next_agent"]


def retry_dispatch_node(state: AgentState) -> dict:
    """
    Pass-through node. Exists only so the Critic's conditional edge has a
    single stable node to route "retry" to, which then fans out (via its
    own conditional edge) to whichever agent originally handled this
    request. Does not modify state — retry_count and critic_feedback
    pass through unchanged from critic_node to the retried agent.
    """
    return {}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("customer_agent", make_agent_node(customer_agent, "customer_agent"))
    graph.add_node("sql_agent", make_agent_node(sql_agent, "sql_agent"))
    graph.add_node("knowledge_agent", make_agent_node(knowledge_agent, "knowledge_agent"))
    graph.add_node("action_agent", make_agent_node(action_agent, "action_agent"))
    graph.add_node("approval_required", approval_required_node)

    graph.add_node("customer_context", customer_context_node)
    graph.add_node("policy_context", policy_context_node)
    graph.add_node("combine_results", combine_results_node)

    graph.add_node("critic", critic_node)
    graph.add_node("retry_dispatch", retry_dispatch_node)
    graph.add_node("give_up", give_up_node)

    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "customer_agent": "customer_agent",
            "sql_agent": "sql_agent",
            "knowledge_agent": "knowledge_agent",
            "action_agent": "action_agent",
            "approval_required": "approval_required",
            "customer_context": "customer_context",
            "policy_context": "policy_context",
        },
    )

    # Single-agent paths now go through the Critic instead of straight to END
    graph.add_edge("customer_agent", "critic")
    graph.add_edge("sql_agent", "critic")
    graph.add_edge("knowledge_agent", "critic")
    graph.add_edge("action_agent", "critic")

    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "end": END,
            "give_up": "give_up",
            "retry": "retry_dispatch",
        },
    )

    # retry_dispatch fans out to whichever agent originally handled this
    # request (next_agent, set by the Supervisor, is untouched by the
    # Critic/retry path — it survives because no node overwrites it here)
    graph.add_conditional_edges(
        "retry_dispatch",
        lambda state: state["next_agent"],
        {
            "customer_agent": "customer_agent",
            "sql_agent": "sql_agent",
            "knowledge_agent": "knowledge_agent",
            "action_agent": "action_agent",
        },
    )

    graph.add_edge("give_up", END)

    # multi_context and approval paths are unaffected by the Critic
    graph.add_edge("customer_context", "combine_results")
    graph.add_edge("policy_context", "combine_results")
    graph.add_edge("combine_results", "approval_required")
    graph.add_edge("approval_required", END)

    pool = ConnectionPool(
        conninfo=settings.database_url,
        max_size=10,
        kwargs={"autocommit": True, "row_factory": dict_row},
    )
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()

    return graph.compile(checkpointer=checkpointer)


compiled_graph = build_graph()