from pydantic import BaseModel, Field
from app.llm.client import get_llm


class RoutingDecision(BaseModel):
    agent: str = Field(
        description="Which agent should handle this: customer_agent, sql_agent, knowledge_agent, or action_agent"
    )
    reason: str = Field(
        description="Brief reason for this routing choice"
    )


llm = get_llm()

structured_llm = llm.with_structured_output(RoutingDecision)

result = structured_llm.invoke(
    "User asked: 'Find customers who have placed more than 5 orders.' "
    "Which agent should handle this?"
)

print("Agent:", result.agent)
print("Reason:", result.reason)
print("Type check:", type(result))