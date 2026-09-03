from app.graph.nodes.first_agent import agent

def ask_with_trace(question: str):
    print(f"\n{'='*60}")
    print(f"USER: {question}")
    print('='*60)

    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    for msg in result["messages"]:
        msg_type = msg.__class__.__name__

        if msg_type == "HumanMessage":
            print(f"\n[HUMAN] {msg.content}")

        elif msg_type == "AIMessage":
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"\n[AGENT DECIDES TO CALL TOOL] {tc['name']}({tc['args']})")
            if msg.content:
                print(f"\n[AGENT FINAL ANSWER] {msg.content}")

        elif msg_type == "ToolMessage":
            print(f"\n[TOOL RESULT] {msg.content}")

ask_with_trace("A customer wants a refund of 8000 for order... actually, first tell me: what tickets does customer 2 have?")


print("\n\n" + "#"*60)
print("MULTI-TURN STATE TEST")
print("#"*60)

conversation = [
    {"role": "user", "content": "What is customer 2's email address?"},
]

result1 = agent.invoke({"messages": conversation})
print("\n[TURN 1 ANSWER]", result1["messages"][-1].content)

conversation = result1["messages"] + [
    {
        "role": "user",
        "content": "Now send them an email with subject 'Test' and body 'This is a follow up.'"
    }
]

result2 = agent.invoke({"messages": conversation})
print("\n[TURN 2 ANSWER]", result2["messages"][-1].content)