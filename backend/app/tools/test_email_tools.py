import logging
logging.basicConfig(level=logging.INFO)


from app.tools.email_tools import send_customer_email
from app.tools.customer_tools import lookup_customer_orders

customer_id = 2
orders = lookup_customer_orders.invoke({"customer_id": customer_id})
delayed_order = next((o for o in orders if o["status"] == "Delayed"), None)

if delayed_order:
    result = send_customer_email.invoke({
        "customer_id": customer_id,
        "subject": "Update on your delayed order",
        "body": f"Your order #{delayed_order['order_id']} (amount: {delayed_order['amount']}) is currently delayed. We apologize for the inconvenience.",
    })
    print("Email result:", result)
else:
    result = send_customer_email.invoke({
        "customer_id": customer_id,
        "subject": "General update",
        "body": "This is a test email with no linked order.",
    })
    print("Email result:", result)

# Invalid customer should fail cleanly
bad_result = send_customer_email.invoke({
    "customer_id": 999999,
    "subject": "Should fail",
    "body": "This customer does not exist.",
})
print("Invalid customer test:", bad_result)