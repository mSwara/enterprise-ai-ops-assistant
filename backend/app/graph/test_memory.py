from app.graph.graph_builder import compiled_graph

THREAD_ID = "test-conversation-1"


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


ask("What is customer 3's email?")
ask("How many orders do they have?")
ask("Now send them an email with subject 'Order Update' and body 'Thank you for your patience.'")