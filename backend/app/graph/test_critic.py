from app.graph.critic import check_groundedness

# CASE 1: Answer is fully grounded — should PASS
print("=== CASE 1: Grounded answer ===")
result1 = check_groundedness(
    answer="Order 238 has status 'Placed' and amount $6,209.69.",
    evidence="Order 238: customer_id=3, amount=6209.69, status=Placed, created_at=2025-10-08",
    original_question="What is the status of order 238?",
)
print("Verdict:", result1.verdict)
print("Issues:", result1.issues)

# CASE 2: Answer invents a fact NOT in evidence — should FAIL
print("\n=== CASE 2: Hallucinated answer (recreating the Phase 7 bug) ===")
result2 = check_groundedness(
    answer="Order 238 was delayed due to a courier issue and will arrive in 3 days.",
    evidence="Order 238: customer_id=3, amount=6209.69, status=Placed, created_at=2025-10-08",
    original_question="Why was order 238 delayed?",
)
print("Verdict:", result2.verdict)
print("Issues:", result2.issues)

# CASE 3: Answer with a wrong NUMBER — should FAIL
print("\n=== CASE 3: Wrong number ===")
result3 = check_groundedness(
    answer="41 customers have placed more than 5 orders, the highest being 15 orders.",
    evidence="Query result: 41 customers with order_count > 5. Max order_count in results: 10.",
    original_question="How many customers have more than 5 orders, and what's the max?",
)
print("Verdict:", result3.verdict)
print("Issues:", result3.issues)