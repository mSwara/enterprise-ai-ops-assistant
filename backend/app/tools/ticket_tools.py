from typing import Optional
from langchain_core.tools import tool
from app.tools.db_tools import create_ticket


@tool
def create_support_ticket(
    customer_id: int,
    subject: str,
    description: str,
    order_id: Optional[int] = None,
) -> dict:
    """
    Create a new support ticket for a customer. Use this when a user asks
    to open, file, log, or create a support ticket or complaint.

    Always set status to 'Open' automatically — do not attempt to set
    ticket status yourself.

    Args:
        customer_id: The ID of the customer this ticket is for. Must be a real, existing customer_id.
        subject: A short summary of the issue, e.g. "Order delayed".
        description: A clear, factual description of the issue, grounded in
            information already retrieved (e.g. order status, delay reason).
            Do not invent details not present in prior tool results.
        order_id: Optional. The related order_id, if this ticket concerns a specific order.
    """
    return create_ticket(
        customer_id=customer_id,
        subject=subject,
        description=description,
        order_id=order_id,
    )