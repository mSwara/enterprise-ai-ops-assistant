from app.tools.customer_tools import (
    lookup_customer,
    lookup_customer_orders,
    lookup_order_payment,
    lookup_customer_tickets,
)

# Direct invocation (bypassing LLM, just confirming the tool wrapper works)
print("Tool name:", lookup_customer.name)
print("Tool description:", lookup_customer.description)
print("Tool args schema:", lookup_customer.args)

result = lookup_customer.invoke({"customer_id": 2})
print("Customer lookup result:", result)

orders = lookup_customer_orders.invoke({"customer_id": 2})
print("Order count for customer 2:", len(orders))