from langchain.agents import create_agent
from app.llm.client import get_llm
from app.tools.customer_tools import (
    lookup_customer,
    lookup_customer_orders,
    lookup_order_payment,
    lookup_customer_tickets,
)
from app.tools.sql_tools import run_sql_query
from app.tools.ticket_tools import create_support_ticket
from app.tools.email_tools import send_customer_email

llm = get_llm()

tools = [
    lookup_customer,
    lookup_customer_orders,
    lookup_order_payment,
    lookup_customer_tickets,
    run_sql_query,
    create_support_ticket,
    send_customer_email,
]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are an enterprise operations assistant. You help staff look up "
        "customer, order, payment, and ticket information, run analytical "
        "queries, create support tickets, and send customer emails. "
        "Always use tools to get real data before answering — never guess "
        "or invent customer, order, or payment details. If a tool returns "
        "an error, tell the user clearly rather than making something up."
    ),
)