from langchain.agents import create_agent

from app.llm.client import get_llm

from app.tools.customer_tools import (
    lookup_customer,
    lookup_customer_orders,
    lookup_order_payment,
    lookup_customer_tickets,
)


customer_agent = create_agent(
    model=get_llm(),
    tools=[
        lookup_customer,
        lookup_customer_orders,
        lookup_order_payment,
        lookup_customer_tickets,
    ],
    system_prompt=(
        "You are the Customer Agent. You retrieve customer profiles, order "
        "history, payment details, and ticket history. You can only READ "
        "data — you cannot create tickets, send emails, or run arbitrary "
        "SQL. Always ground your answers in tool results. Never invent "
        "customer or order details."
    ),
)