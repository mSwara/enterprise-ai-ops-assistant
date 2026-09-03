from app.tools.ticket_tools import create_support_ticket
from app.tools.customer_tools import lookup_customer_orders

# Use a real customer/order from your seeded data
customer_id = 2
orders = lookup_customer_orders.invoke({"customer_id": customer_id})
delayed_order = next((o for o in orders if o["status"] == "Delayed"), None)

if delayed_order:
    result = create_support_ticket.invoke({
        "customer_id": customer_id,
        "subject": "Order delayed",
        "description": f"Customer's order #{delayed_order['order_id']} is delayed. Order amount: {delayed_order['amount']}.",
        "order_id": delayed_order["order_id"],
    })
    print("Created ticket:", result)
else:
    print("No delayed order found for this customer — trying without order_id")
    result = create_support_ticket.invoke({
        "customer_id": customer_id,
        "subject": "General inquiry",
        "description": "Test ticket with no linked order.",
    })
    print("Created ticket:", result)

# Test validation: invalid customer_id should fail cleanly
bad_result = create_support_ticket.invoke({
    "customer_id": 999999,
    "subject": "Should fail",
    "description": "This customer does not exist.",
})
print("Invalid customer test:", bad_result)

