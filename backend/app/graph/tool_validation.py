import re
import json


def extract_tool_errors(messages: list) -> list[dict]:
    """
    Scans a list of LangChain messages for ToolMessage entries whose content
    indicates a failed tool call (e.g. {"success": false, "error": "..."}
    from run_sql_query, or a Python exception string leaking through).

    This catches the Phase 9 SQL-dialect-crash class of problem: even after
    that specific bug was fixed (Step 9.4's broad exception handling), any
    NEW tool could fail the same way in the future, and this scan is a
    general-purpose safety net rather than a fix for one specific tool.
    """
    errors = []

    for msg in messages:
        msg_type = msg.__class__.__name__
        if msg_type != "ToolMessage":
            continue

        content = msg.content
        tool_name = getattr(msg, "name", "unknown_tool")

        # Case 1: tool returned a JSON-like dict with an explicit failure flag
        if isinstance(content, str):
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict) and parsed.get("success") is False:
                    errors.append({
                        "tool": tool_name,
                        "error": parsed.get("error", "Unknown tool failure"),
                    })
                    continue
            except (json.JSONDecodeError, TypeError):
                pass

        # Case 2: raw error-shaped string leaked through (e.g. {"error": "..."})
        if isinstance(content, str) and re.search(r'"error"\s*:', content):
            errors.append({"tool": tool_name, "error": content[:300]})

    return errors