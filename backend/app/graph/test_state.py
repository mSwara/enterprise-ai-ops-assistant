from app.graph.state import AgentState

# Simulate what an initial state looks like when a user sends a message
initial_state: AgentState = {
    "messages": [{"role": "user", "content": "Where is order 5?"}],
    "next_agent": None,
    "findings": {},
    "validated": None,
    "requires_approval": None,
    "approved": None,
}

print("Initial state keys:", list(initial_state.keys()))
print("Messages:", initial_state["messages"])
print("Findings (empty dict, ready to be filled by agents):", initial_state["findings"])