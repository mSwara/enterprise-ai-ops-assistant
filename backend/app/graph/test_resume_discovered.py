from app.graph.approvals import resume_approval

result = resume_approval(
    thread_id="5b91d8a0-0729-42ad-91b6-78da729bd4e5",
    approved=False,
    note="Amount exceeds standard authorization; escalate to finance.",
)

print("APPROVED:", result.get("approved"))
print("FINAL MESSAGE:", result["messages"][-1].content)