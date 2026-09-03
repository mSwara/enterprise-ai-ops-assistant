from app.graph.graph_builder import compiled_graph

THREAD_ID = "persistent-test-1"


def ask(question: str):
    print(f"\n--- USER: {question} ---")

    config = {"configurable": {"thread_id": THREAD_ID}}

    result = compiled_graph.invoke(
        {
            "messages": [{"role": "user", "content": question}],
            "next_agent": None,
            "findings": {},
            "validated": None,
            "requires_approval": None,
            "approved": None,
        },
        config=config,
    )

    print("FINAL MESSAGE:", result["messages"][-1].content)
    print("Total messages in state:", len(result["messages"]))


if __name__ == "__main__":
    ask("What is customer 5's email?")