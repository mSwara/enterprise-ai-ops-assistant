import uuid
from app.graph.graph_builder import compiled_graph


def run_query(question: str):
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
    return result


class TestCustomerLookupScenario:
    def test_customer_3_email_and_orders(self):
        result = run_query("What is customer 3's email and how many orders do they have?")
        reply = result["messages"][-1].content
        assert "thompsonchase@example.com" in reply
        assert "4" in reply  # 4 orders, known from seed data
        assert result.get("validated") is True


class TestAnalyticalScenario:
    def test_customers_with_more_than_5_orders(self):
        result = run_query("Find customers who have placed more than 5 orders.")
        reply = result["messages"][-1].content
        assert "41" in reply  # known correct count from Phase 4 testing
        assert result.get("validated") is True


class TestPolicyScenario:
    def test_electronics_return_policy(self):
        result = run_query("What is our return policy for electronics?")
        reply = result["messages"][-1].content
        assert "15" in reply  # 15-day return window
        assert "return_policy.txt" in reply
        assert result.get("validated") is True


class TestActionScenario:
    def test_create_ticket_for_delayed_order(self):
        result = run_query("Create a support ticket for customer 3's delayed order.")
        reply = result["messages"][-1].content
        assert "Ticket ID" in reply or "ticket" in reply.lower()
        assert result.get("validated") is True


class TestSensitiveRefundScenario:
    def test_refund_over_threshold_requires_approval(self):
        result = run_query("A customer wants a refund of 8000. Should I approve it?")
        assert "__interrupt__" in result  # must pause, never auto-execute
        assert result.get("requires_approval") is True