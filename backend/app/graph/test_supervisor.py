from app.graph.supervisor import route_request

test_queries = [
    "Where is order for customer 3?",
    "Find customers who have placed more than 5 orders.",
    "What is our return policy for electronics?",
    "Create a support ticket for customer 3's delayed order.",
    "A customer wants a refund of 8000. Should I approve it?",
    "Send an email to customer 3 explaining their order status.",
]

for q in test_queries:
    decision = route_request(q)
    print(f"\nQUERY: {q}")
    print(f"  -> agent: {decision.agent}")
    print(f"  -> reason: {decision.reason}")
    print(f"  -> is_sensitive: {decision.is_sensitive}")