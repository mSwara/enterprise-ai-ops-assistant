import time
from app.graph.graph_builder import compiled_graph

def ask(question: str, thread_id: str):
    print(f"\n{'='*60}")
    print(f"USER: {question}")
    print('='*60)
    config = {"configurable": {"thread_id": thread_id}}
    start = time.time()
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
    elapsed = time.time() - start
    print("ROUTED TO:", result.get("next_agent"))
    print("REQUIRES APPROVAL:", result.get("requires_approval"))
    print("FINDINGS KEYS:", list(result.get("findings", {}).keys()))
    print(f"TIME: {elapsed:.2f}s")
    print("FINAL MESSAGE:", result["messages"][-1].content)


ask("Customer 3 wants a refund of 8000 for order 238. Should I approve it?", "parallel-test-1")