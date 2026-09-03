from langchain_core.tools import tool
from app.tools.db_tools import (
    get_customer,
    get_customer_orders,
    get_order_payment,
    get_customer_tickets,
)


@tool
def lookup_customer(customer_id: int) -> dict:
    """Look up a customer's basic profile (name, email, phone) by their customer_id."""
    return get_customer(customer_id)


@tool
def lookup_customer_orders(customer_id: int) -> list:
    """Retrieve all orders placed by a specific customer, given their customer_id."""
    return get_customer_orders(customer_id)


@tool
def lookup_order_payment(order_id: int) -> dict:
    """Retrieve payment details (amount, method, status) for a specific order_id."""
    return get_order_payment(order_id)


@tool
def lookup_customer_tickets(customer_id: int) -> list:
    """Retrieve all support tickets filed by a specific customer, given their customer_id."""
    return get_customer_tickets(customer_id)