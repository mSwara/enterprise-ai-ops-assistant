from app.graph.graph_builder import compiled_graph
def ask(question: str):
    print(f"\n{'='*60}")
    print(f"USER: {question}")
    print('='*60)

    initial_state = {
        "messages": [{"role": "user", "content": question}],
        "next_agent": None,
        "findings": {},
        "validated": None,
        "requires_approval": None,
        "approved": None,
    }
    

    config = {"configurable": {"thread_id": f"regression-test-{question}"}}

    result = compiled_graph.invoke(

        initial_state,
        config=config,
    )

    print("ROUTED TO:", result.get("next_agent"))
    print("REQUIRES APPROVAL:", result.get("requires_approval"))
    print("ROUTING REASON:", result.get("findings", {}).get("routing_reason"))
    print("FINAL MESSAGE:", result["messages"][-1].content)


ask("Where is order info for customer 3?")
ask("Find customers who have placed more than 5 orders.")
ask("What is our return policy for electronics?")
ask("Create a support ticket for customer 3's delayed order.")
ask("A customer wants a refund of 8000. Should I approve it?")
ask("Why was order 238 delayed?")
ask("Give me a summary of today's unresolved customer complaints.")
ask("Send an email to customer 3 explaining the delay.")
ask("A customer wants a refund of 8000. Should I approve it?")