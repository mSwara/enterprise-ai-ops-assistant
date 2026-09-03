from langchain_core.tools import tool
from app.tools.db_tools import send_email


@tool
def send_customer_email(customer_id: int, subject: str, body: str) -> dict:
    """
    Send an email to a customer. This is SIMULATED — no real email is sent;
    the message is logged and a confirmation is returned. Use this when a
    user asks to email, notify, or inform a customer about something.

    Args:
        customer_id: The ID of the customer to email. Must be a real, existing customer_id.
        subject: A short, clear email subject line.
        body: The email body. Must be grounded in information already retrieved
            via other tools (e.g. order status, delay reason, ticket details).
            Do not invent order details, dates, or promises not confirmed by
            prior tool results.
    """
    return send_email(customer_id=customer_id, subject=subject, body=body)