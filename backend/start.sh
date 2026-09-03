#!/bin/bash
set -e

# Start the MCP server in the background
python -m app.mcp.mcp_server &

# Give it a moment to start before FastAPI tries to connect (Customer Agent
# loads MCP tools at import time — see Step 9.3 — so MCP must be ready
# before the app starts serving requests)
sleep 3

# Start FastAPI in the foreground (this is what keeps the container running)
exec uvicorn app.main:app --host 0.0.0.0 --port 8000