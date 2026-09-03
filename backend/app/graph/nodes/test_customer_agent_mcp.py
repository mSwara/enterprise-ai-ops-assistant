from app.graph.nodes.customer_agent import customer_agent


def ask(question: str):
    print(f"\n--- {question} ---")
    result = customer_agent.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })
    print(result["messages"][-1].content)


ask("What is customer 3's email and how many orders do they have?")