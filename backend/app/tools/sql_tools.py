from langchain_core.tools import tool
from app.db.safe_query import run_safe_query, UnsafeQueryError


@tool
def run_sql_query(sql: str) -> dict:
    """
    Execute a read-only SQL SELECT query against the enterprise database
    (PostgreSQL syntax; tables: customers, orders, payments, tickets).

    Only SELECT statements are allowed. Any query containing DROP, DELETE,
    UPDATE, INSERT, ALTER, TRUNCATE, or multiple stacked statements will be
    rejected before execution.

    IMPORTANT: This database is PostgreSQL. Use PostgreSQL syntax, e.g.
    CURRENT_DATE (not DATE('now')), STRING_AGG (not GROUP_CONCAT).

    Use this for analytical questions that require filtering, grouping,
    counting, or joining data.
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