import uuid
from app.graph.graph_builder import compiled_graph


def ask(question: str):
    print(f"\n{'='*60}\nUSER: {question}\n{'='*60}")
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    result = compiled_graph.invoke(
        {
            "messages": [{"role": "user", "content": question}],
            "next_agent": None, "findings": {}, "validated": None,
            "requires_approval": None, "approved": None,
            "retry_count": 0, "critic_feedback": None,
            "latest_attempt_messages": None,
        },
        config=config,
    )
    print("VALIDATED:", result.get("validated"))
    print("RETRY COUNT:", result.get("retry_count"))
    print("FINAL:", result["messages"][-1].content)


ask("What is customer 3's email and how many orders do they have?")
ask("Find customers who have placed more than 5 orders.")
ask("What is our policy on international returns via drone delivery?")