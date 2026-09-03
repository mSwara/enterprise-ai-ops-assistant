from app.db.safe_query import run_safe_query

print("Customer count:", run_safe_query("SELECT COUNT(*) as count FROM customers"))
print("Order count:", run_safe_query("SELECT COUNT(*) as count FROM orders"))
print("Order status breakdown:", run_safe_query(
    "SELECT status, COUNT(*) as count FROM orders GROUP BY status"
))
print("Sample customers:", run_safe_query("SELECT customer_id, name, email FROM customers LIMIT 3"))