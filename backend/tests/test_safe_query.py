from app.db.safe_query import is_query_safe, run_safe_query, UnsafeQueryError


class TestIsQuerySafe:
    def test_allows_simple_select(self):
        assert is_query_safe("SELECT * FROM customers") is True

    def test_allows_select_with_join(self):
        sql = "SELECT c.name, o.amount FROM customers c JOIN orders o ON c.customer_id = o.customer_id"
        assert is_query_safe(sql) is True

    def test_blocks_drop(self):
        assert is_query_safe("DROP TABLE customers") is False

    def test_blocks_delete(self):
        assert is_query_safe("DELETE FROM orders WHERE order_id = 1") is False

    def test_blocks_update(self):
        assert is_query_safe("UPDATE customers SET name = 'hacked'") is False

    def test_blocks_insert(self):
        assert is_query_safe("INSERT INTO customers (name) VALUES ('x')") is False

    def test_blocks_stacked_statements(self):
        assert is_query_safe("SELECT * FROM customers; DROP TABLE orders;") is False

    def test_blocks_keyword_hidden_in_subquery(self):
        sql = "SELECT * FROM customers WHERE customer_id IN (DELETE FROM orders RETURNING customer_id)"
        assert is_query_safe(sql) is False

    def test_case_insensitive_blocking(self):
        assert is_query_safe("dRoP TABLE customers") is False


class TestRunSafeQuery:
    def test_executes_real_select(self):
        rows = run_safe_query("SELECT COUNT(*) as count FROM customers")
        assert len(rows) == 1
        assert rows[0]["count"] > 0  # depends on Phase 2 seed data being present

    def test_raises_on_unsafe_query(self):
        try:
            run_safe_query("DELETE FROM customers")
            assert False, "Expected UnsafeQueryError to be raised"
        except UnsafeQueryError:
            pass  # expected

    def test_respects_limit(self):
        rows = run_safe_query("SELECT * FROM orders", limit=5)
        assert len(rows) <= 5