from app.graph.approvals import list_pending_approvals


pending = list_pending_approvals()

print(f"Found {len(pending)} pending approval(s):\n")

for p in pending:
    print(f"Thread: {p['thread_id']}")
    print(f"  Request: {p['payload'].get('request')}")
    print(f"  Reason: {p['payload'].get('reason')}")
    print(f"  Recommendation: {p['payload'].get('recommendation')}")
    print()