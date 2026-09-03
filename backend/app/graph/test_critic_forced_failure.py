from app.graph.critic import check_groundedness
from app.graph.tool_validation import extract_tool_errors
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage

# Simulate what critic_node sees on a genuinely bad attempt:
# real tool evidence that CONTRADICTS the agent's final answer.
recent_messages = [
    HumanMessage(content="Why was order 238 delayed?"),
    ToolMessage(
        content='{"order_id": 238, "customer_id": 3, "status": "Placed", "amount": 6209.69}',
        name="lookup_customer_orders",
        tool_call_id="1",
    ),
    AIMessage(content="Order 238 was delayed due to a courier issue and will arrive within 3 days."),
]

print("=== Tool error check (should be empty — tool succeeded) ===")
print(extract_tool_errors(recent_messages))

print("\n=== Groundedness check (should FAIL — answer invents delay details) ===")
evidence = "\n".join(m.content for m in recent_messages if m.__class__.__name__ == "ToolMessage")
verdict = check_groundedness(
    answer=recent_messages[-1].content,
    evidence=evidence,
    original_question=recent_messages[0].content,
)
print("Verdict:", verdict.verdict)
print("Issues:", verdict.issues)