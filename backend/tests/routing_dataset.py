# Each entry: (question, expected_agent)
# Expected agents chosen based on the actual documented purpose of each
# path (Phase 7's supervisor.py descriptions), not just what happened to
# fire in past manual tests.
ROUTING_TEST_CASES = [
    ("What is customer 3's email?", "customer_agent"),
    ("Show me the order history for customer 5.", "customer_agent"),
    ("What tickets has customer 2 filed?", "customer_agent"),
    ("Find customers who have placed more than 5 orders.", "sql_agent"),
    ("How many total orders are in the database?", "sql_agent"),
    ("What is the average order amount?", "sql_agent"),
    ("What is our return policy for electronics?", "knowledge_agent"),
    ("What payment methods do we accept?", "knowledge_agent"),
    ("How long does standard shipping take?", "knowledge_agent"),
    ("Create a support ticket for customer 4 about a late delivery.", "action_agent"),
    ("Send an email to customer 6 confirming their order shipped.", "action_agent"),
    ("A customer wants a refund of 8000 for order 238. Should I approve it?", "multi_context"),
    ("Customer 7 is requesting cancellation and a $3000 refund — what should I do?", "multi_context"),
]