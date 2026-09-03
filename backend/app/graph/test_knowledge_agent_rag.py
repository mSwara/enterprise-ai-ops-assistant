from app.graph.nodes.knowledge_agent import knowledge_agent


def ask(question: str):
    print(f"\n--- {question} ---")
    result = knowledge_agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    print(result["messages"][-1].content)


ask("What is our return policy for electronics?")
ask("A customer wants a refund of 8000. Should I approve it?")
ask("What is the standard shipping time?")
ask("What payment methods are accepted?")