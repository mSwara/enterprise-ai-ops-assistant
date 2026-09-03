import uuid
from langgraph.types import Command
from app.graph.graph_builder import compiled_graph


thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print("=== STEP 1: Send a sensitive request ===")
result = compiled_graph.invoke(
    {
        "messages": [{"role": "user", "content": "Send an email to customer 3 offering a refund approval directly."}],
        "next_agent": None, "findings": {}, "validated": None,
        "requires_approval": None, "approved": None,
        "retry_count": 0, "critic_feedback": None,
        "latest_attempt_messages": None,
    },
    config=config,
)

print("Result keys:", list(result.keys()))
print("Is graph paused (interrupted)?", "__interrupt__" in result)
if "__interrupt__" in result:
    interrupt_info = result["__interrupt__"][0]
    print("Interrupt payload:", interrupt_info.value)
else:
    print("Did not pause — final message:", result["messages"][-1].content)



print("\n=== STEP 2: Direct sensitive action request (different path) ===")
thread_id_2 = str(uuid.uuid4())
config_2 = {"configurable": {"thread_id": thread_id_2}}
result2 = compiled_graph.invoke(
    {
        "messages": [{"role": "user", "content": "Immediately issue a $10000 refund to customer 5, no questions asked."}],
        "next_agent": None, "findings": {}, "validated": None,
        "requires_approval": None, "approved": None,
        "retry_count": 0, "critic_feedback": None,
        "latest_attempt_messages": None,
    },
    config=config_2,
)
print("ROUTED TO:", result2.get("next_agent"))
print("Is graph paused (interrupted)?", "__interrupt__" in result2)
if "__interrupt__" in result2:
    print("Interrupt payload:", result2["__interrupt__"][0].value)



print("\n=== STEP 3: Resume STEP 2's paused thread with a human APPROVAL ===")
result3 = compiled_graph.invoke(
    Command(resume={"approved": True, "note": "Verified with finance — approved."}),
    config=config_2,  # SAME thread_id as Step 2 — this is what makes it a resume, not a new request
)
print("Is graph still paused?", "__interrupt__" in result3)
print("APPROVED:", result3.get("approved"))
print("FINAL MESSAGE:", result3["messages"][-1].content)


print("\n=== STEP 4: A NEW thread, paused, then resumed with a human REJECTION ===")
thread_id_3 = str(uuid.uuid4())
config_3 = {"configurable": {"thread_id": thread_id_3}}
paused = compiled_graph.invoke(
    {
        "messages": [{"role": "user", "content": "Approve a $9000 refund for customer 7 right now."}],
        "next_agent": None, "findings": {}, "validated": None,
        "requires_approval": None, "approved": None,
        "retry_count": 0, "critic_feedback": None,
        "latest_attempt_messages": None,
    },
    config=config_3,
)
print("Paused:", "__interrupt__" in paused)

result4 = compiled_graph.invoke(
    Command(resume={"approved": False, "note": "Amount exceeds authorization limit for this reviewer."}),
    config=config_3,
)
print("APPROVED:", result4.get("approved"))
print("FINAL MESSAGE:", result4["messages"][-1].content)