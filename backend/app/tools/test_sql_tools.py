from app.tools.sql_tools import run_sql_query

# A safe analytical query
result = run_sql_query.invoke({
    "sql": "SELECT customer_id, COUNT(*) as order_count FROM orders GROUP BY customer_id HAVING COUNT(*) > 5"
})
print("Analytical query result:", result)

# An unsafe query — should be rejected, not executed
blocked = run_sql_query.invoke({
    "sql": "DELETE FROM customers"
})
print("Blocked query result:", blocked)