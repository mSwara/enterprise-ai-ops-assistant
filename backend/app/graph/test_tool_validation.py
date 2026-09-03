from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from app.graph.tool_validation import extract_tool_errors

# CASE 1: No errors — clean tool results
clean_messages = [
    HumanMessage(content="How many customers do we have?"),
    ToolMessage(content='{"success": true, "rows": [{"count": 200}], "row_count": 1}', name="run_sql_query", tool_call_id="1"),
    AIMessage(content="There are 200 customers."),
]
print("CASE 1 (clean):", extract_tool_errors(clean_messages))

# CASE 2: A failed SQL query (recreating the Phase 9 bug shape)
failed_messages = [
    HumanMessage(content="Summarize today's complaints."),
    ToolMessage(
        content='{"success": false, "error": "Query failed: function group_concat(character varying) does not exist"}',
        name="run_sql_query",
        tool_call_id="2",
    ),
    AIMessage(content="Here is a summary of today's complaints: ..."),
]
print("CASE 2 (failed tool, Phase 9 shape):", extract_tool_errors(failed_messages))

# CASE 3: Multiple tool calls, one fails
mixed_messages = [
    HumanMessage(content="Look up customer 3 and create a ticket."),
    ToolMessage(content='{"customer_id": 3, "name": "Jeremy Gomez"}', name="lookup_customer", tool_call_id="3"),
    ToolMessage(content='{"error": "Customer 999999 not found"}', name="create_support_ticket", tool_call_id="4"),
    AIMessage(content="Ticket created successfully."),
]
print("CASE 3 (mixed, one fails):", extract_tool_errors(mixed_messages))