from app.graph.nodes.first_agent import agent

def ask(question: str):
    print(f"\n--- USER: {question} ---")
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    final_message = result["messages"][-1]
    print("AGENT:", final_message.content)

ask("Where is order for customer 2? Give me their order history.")
ask("Find customers who have placed more than 5 orders. Just tell me how many such customers exist.")