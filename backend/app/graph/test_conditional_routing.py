from app.graph.graph_builder import compiled_graph

def ask(question: str):
    print(f"\n--- USER: {question} ---")
    initial_state = {
        "messages": [{"role": "user", "content": question}],
        "next_agent": None,
        "findings": {},
        "validated": None,
        "requires_approval": None,
        "approved": None,
    }
    result = compiled_graph.invoke(initial_state)

    if result.get("requires_approval"):
        print("ROUTED TO: flag_for_approval (blocked for human review)")
        print("requires_approval:", result["requires_approval"])
    else:
        print("ROUTED TO: agent (handled normally)")
        print("FINAL ANSWER:", result["messages"][-1].content)

ask("What is customer 3's email?")
ask("A customer wants a refund of 8000 for their order. Can you approve it?")