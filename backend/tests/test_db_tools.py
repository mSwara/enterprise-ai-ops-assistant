from app.tools.db_tools import (
    get_customer,
    get_customer_orders,
    create_ticket,
    send_email,
)


class TestGetCustomer:
    def test_returns_real_customer(self):
        result = get_customer(3)
        assert "error" not in result
        assert result["customer_id"] == 3
        assert "@" in result["email"]

    def test_returns_error_for_nonexistent_customer(self):
        result = get_customer(999999)
        assert "error" in result


class TestGetCustomerOrders:
    def test_returns_list_for_real_customer(self):
        orders = get_customer_orders(3)
        assert isinstance(orders, list)
        assert len(orders) > 0
        assert all("order_id" in o for o in orders)

    def test_returns_empty_list_for_nonexistent_customer(self):
        orders = get_customer_orders(999999)
        assert orders == []


class TestCreateTicket:
    def test_creates_ticket_for_valid_customer(self):
        result = create_ticket(
            customer_id=3,
            subject="Automated test ticket",
            description="Created by pytest — safe to ignore/delete.",
        )
        assert "error" not in result
        assert result["status"] == "Open"
        assert result["customer_id"] == 3

    def test_rejects_invalid_customer(self):
        result = create_ticket(
            customer_id=999999,
            subject="Should fail",
            description="Invalid customer test",
        )
        assert "error" in result

    def test_rejects_invalid_order_id(self):
        result = create_ticket(
            customer_id=3,
            subject="Should fail",
            description="Invalid order test",
            order_id=999999,
        )
        assert "error" in result


class TestSendEmail:
    def test_sends_to_valid_customer(self):
        result = send_email(customer_id=3, subject="Test", body="Automated test email.")
        assert result["status"] == "sent"
        assert "@" in result["to"]

    def test_rejects_invalid_customer(self):
        result = send_email(customer_id=999999, subject="Test", body="Should fail")
        assert "error" in result