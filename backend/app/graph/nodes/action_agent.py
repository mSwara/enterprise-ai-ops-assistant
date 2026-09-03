from langchain.agents import create_agent
from app.llm.client import get_llm
from app.tools.ticket_tools import create_support_ticket
from app.tools.email_tools import send_customer_email

action_agent = create_agent(
    model=get_llm(),
    tools=[create_support_ticket, send_customer_email],
    system_prompt=(
        "You are the Action Agent. You create support tickets and send "
        "customer emails. You can only take these two actions — you "
        "cannot look up new information yourself. Base ticket descriptions "
        "and email content ONLY on information already provided to you in "
        "the conversation. Never invent order details, amounts, or dates "
        "that were not explicitly given to you."
    ),
)