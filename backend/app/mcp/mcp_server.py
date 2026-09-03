from mcp.server.fastmcp import FastMCP

from app.tools.db_tools import (
    get_customer,
    get_customer_orders,
    get_order_payment,
    get_customer_tickets,
    create_ticket,
    send_email,
)
from app.db.safe_query import run_safe_query, UnsafeQueryError
from app.rag.ingest import get_vector_store


mcp = FastMCP("EnterpriseOpsTools")


@mcp.tool()
def lookup_customer(customer_id: int) -> dict:
    """Look up a customer's basic profile by customer_id."""
    return get_customer(customer_id)


@mcp.tool()
def lookup_customer_orders(customer_id: int) -> list:
    """Retrieve all orders for a customer."""
    return get_customer_orders(customer_id)


@mcp.tool()
def lookup_order_payment(order_id: int) -> dict:
    """Retrieve payment details for an order."""
    return get_order_payment(order_id)


@mcp.tool()
def lookup_customer_tickets(customer_id: int) -> list:
    """Retrieve all support tickets for a customer."""
    return get_customer_tickets(customer_id)


@mcp.tool()
def run_sql_query(sql: str) -> dict:
    """
    Execute a read-only SQL SELECT query against the enterprise database
    using PostgreSQL syntax.

    Only SELECT statements are allowed.
    Use CURRENT_DATE instead of DATE('now') and STRING_AGG
    instead of GROUP_CONCAT.
    """
    try:
        rows = run_safe_query(sql)
        return {
            "success": True,
            "rows": rows,
            "row_count": len(rows),
        }

    except UnsafeQueryError as e:
        return {
            "success": False,
            "error": str(e),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Query failed: {str(e)}",
        }


@mcp.tool()
def create_support_ticket(
    customer_id: int,
    subject: str,
    description: str,
    order_id: int = None,
) -> dict:
    """Create a support ticket for a customer."""
    return create_ticket(
        customer_id=customer_id,
        subject=subject,
        description=description,
        order_id=order_id,
    )


@mcp.tool()
def send_customer_email(
    customer_id: int,
    subject: str,
    body: str,
) -> dict:
    """Send a simulated email to a customer."""
    return send_email(
        customer_id=customer_id,
        subject=subject,
        body=body,
    )


@mcp.tool()
def search_knowledge_base(query: str) -> dict:
    """Search company policy and support documents."""
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=3)

    if not results:
        return {
            "found": False,
            "chunks": [],
        }

    return {
        "found": True,
        "chunks": [
            {
                "source": doc.metadata.get("source", "unknown"),
                "content": doc.page_content,
            }
            for doc in results
        ],
    }


# Use a different port because 8000 is already occupied.
mcp.settings.port = 8001


if __name__ == "__main__":
    mcp.run(transport="streamable-http")