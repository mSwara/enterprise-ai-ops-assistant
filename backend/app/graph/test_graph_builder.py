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
    print("FINAL ANSWER:", result["messages"][-1].content)
    print("Total messages in state:", len(result["messages"]))

ask("What is customer 3's email and how many orders do they have?")