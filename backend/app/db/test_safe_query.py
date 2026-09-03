from app.db.safe_query import run_safe_query, is_query_safe, UnsafeQueryError

print("SELECT test:", is_query_safe("SELECT * FROM customers"))
print("DROP test:", is_query_safe("DROP TABLE customers"))
print("DELETE test:", is_query_safe("DELETE FROM orders WHERE order_id=1"))
print("Stacked test:", is_query_safe("SELECT * FROM customers; DROP TABLE orders;"))

rows = run_safe_query("SELECT customer_id, name, email FROM customers LIMIT 3")
print("Sample rows:", rows)

try:
    run_safe_query("DELETE FROM customers")
except UnsafeQueryError as e:
    print("Correctly blocked:", e)