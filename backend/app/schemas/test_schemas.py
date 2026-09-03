from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.approval import PendingApproval, ApprovalDecisionRequest

# Valid request
req = ChatRequest(message="What is customer 3's email?")
print("ChatRequest (no thread_id):", req)

req2 = ChatRequest(message="Hello", thread_id="abc-123")
print("ChatRequest (with thread_id):", req2)

# Should FAIL validation — empty message
try:
    bad_req = ChatRequest(message="")
    print("ERROR: empty message should have failed validation")
except Exception as e:
    print("Correctly rejected empty message:", type(e).__name__)

# Response shape
resp = ChatResponse(
    thread_id="abc-123",
    reply="Customer 3's email is thompsonchase@example.com",
    paused=False,
)
print("ChatResponse:", resp)

# Approval decision
decision = ApprovalDecisionRequest(approved=True, note="Looks good")
print("ApprovalDecisionRequest:", decision)