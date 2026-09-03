from app.llm.client import get_llm

llm = get_llm()

response = llm.invoke(
    "In one sentence, what does a supervisor agent do in a multi-agent system?"
)

print("Response:", response.content)