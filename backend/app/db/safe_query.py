import re
from sqlalchemy import text
from app.db.session import SessionLocal

ALLOWED_START = ("select",)

BLOCKED_KEYWORDS = (
    "drop", "delete", "update", "insert", "alter",
    "truncate", "grant", "revoke", "create", "replace"
)

class UnsafeQueryError(Exception):
    pass


def is_query_safe(sql: str) -> bool:
    cleaned = sql.strip().lower()

    if not cleaned.startswith(ALLOWED_START):
        return False

    if cleaned.rstrip(";").count(";") > 0:
        return False

    for word in BLOCKED_KEYWORDS:
        if re.search(rf"\b{word}\b", cleaned):
            return False

    return True


def run_safe_query(sql: str, limit: int = 100):
    """
    Executes a SELECT-only query. Raises UnsafeQueryError if the query
    isn't a clean, single, read-only SELECT statement.
    """
    if not is_query_safe(sql):
        raise UnsafeQueryError(f"Blocked unsafe query: {sql}")

    
    session = SessionLocal()
    try:
        result = session.execute(text(sql))
        rows = result.fetchmany(limit)
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        session.close()