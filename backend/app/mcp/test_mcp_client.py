import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient(
        {
            "enterprise_tools": {
                "url": "http://127.0.0.1:8001/mcp",
                "transport": "streamable_http",
            }
        }
    )

    tools = await client.get_tools()

    print("Discovered tools:", [tool.name for tool in tools])

    # Test customer lookup through MCP
    lookup_tool = next(
        tool for tool in tools
        if tool.name == "lookup_customer"
    )

    result = await lookup_tool.ainvoke({
        "customer_id": 2
    })

    print("lookup_customer(2) via MCP:", result)

    # Test read-only SQL query through MCP
    sql_tool = next(
        tool for tool in tools
        if tool.name == "run_sql_query"
    )

    sql_result = await sql_tool.ainvoke({
        "sql": "SELECT COUNT(*) as count FROM customers"
    })

    print("run_sql_query via MCP:", sql_result)


if __name__ == "__main__":
    asyncio.run(main())