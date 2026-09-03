from app.graph.nodes.customer_agent import customer_agent
from app.graph.nodes.sql_agent import sql_agent
from app.graph.nodes.action_agent import action_agent
from app.graph.nodes.knowledge_agent import knowledge_agent


def ask(agent, label, question):
    print(f"\n--- {label}: {question} ---")
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    print("ANSWER:", result["messages"][-1].content)


ask(customer_agent, "CUSTOMER AGENT", "What orders does customer 3 have?")
ask(sql_agent, "SQL AGENT", "How many customers have placed more than 5 orders?")
ask(knowledge_agent, "KNOWLEDGE AGENT", "What is our return policy for electronics?")

# Confirm the Action Agent CANNOT look up data itself — it has no lookup tools
ask(action_agent, "ACTION AGENT (should refuse to guess)", "Send an email to customer 3 about their order status.")