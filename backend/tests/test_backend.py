"""
Tests for NL-SQL Analyst backend.
Run: pytest tests/ -v
"""
import sys
import os
import pandas as pd
import pytest

# Ensure backend package is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.sql_safety import validate_sql, clean_sql
from app.db.connection import get_schema, get_schema_as_text, get_row_counts
from app.services.chart_service import suggest_chart
from app.services.query_service import execute_raw_sql


# ── SQL Safety Tests ─────────────────────────────────────────────────────────

class TestSQLSafety:

    def test_valid_select(self):
        ok, msg = validate_sql("SELECT * FROM orders")
        assert ok, msg

    def test_valid_cte(self):
        ok, msg = validate_sql("WITH cte AS (SELECT * FROM orders) SELECT * FROM cte")
        assert ok, msg

    def test_rejects_drop(self):
        ok, _ = validate_sql("DROP TABLE orders")
        assert not ok

    def test_rejects_delete(self):
        ok, _ = validate_sql("DELETE FROM orders WHERE order_id = 1")
        assert not ok

    def test_rejects_insert(self):
        ok, _ = validate_sql("INSERT INTO orders VALUES (1,2,3)")
        assert not ok

    def test_rejects_update(self):
        ok, _ = validate_sql("UPDATE orders SET status='cancelled'")
        assert not ok

    def test_rejects_multiple_statements(self):
        ok, _ = validate_sql("SELECT 1; SELECT 2")
        assert not ok

    def test_rejects_empty(self):
        ok, _ = validate_sql("")
        assert not ok

    def test_rejects_pragma(self):
        ok, _ = validate_sql("PRAGMA table_info(orders)")
        assert not ok

    def test_case_insensitive_reject(self):
        ok, _ = validate_sql("drop table orders")
        assert not ok

    def test_clean_sql_strips_backticks(self):
        sql = "```sql\nSELECT * FROM orders\n```"
        assert clean_sql(sql) == "SELECT * FROM orders"

    def test_clean_sql_strips_semicolon(self):
        sql = "SELECT * FROM orders;"
        assert clean_sql(sql) == "SELECT * FROM orders"

    def test_clean_sql_strips_whitespace(self):
        sql = "  SELECT 1  "
        assert clean_sql(sql) == "SELECT 1"


# ── Database / Schema Tests ──────────────────────────────────────────────────

class TestDatabase:

    def test_schema_has_expected_tables(self):
        schema = get_schema()
        for expected in ["customers", "products", "orders", "order_items", "sales_reps"]:
            assert expected in schema, f"Missing table: {expected}"

    def test_schema_has_columns(self):
        schema = get_schema()
        orders_cols = [c["name"] for c in schema["orders"]]
        for col in ["order_id", "customer_id", "order_date", "status", "total_amount"]:
            assert col in orders_cols

    def test_row_counts_nonzero(self):
        counts = get_row_counts()
        assert counts["customers"] >= 500
        assert counts["orders"] >= 3000
        assert counts["order_items"] >= 5000

    def test_schema_as_text_contains_create(self):
        text = get_schema_as_text()
        assert "CREATE TABLE customers" in text
        assert "CREATE TABLE orders" in text

    def test_schema_as_text_contains_columns(self):
        text = get_schema_as_text()
        assert "customer_id" in text
        assert "total_amount" in text


# ── SQL Execution Tests ──────────────────────────────────────────────────────

class TestQueryExecution:

    def test_simple_count(self):
        result = execute_raw_sql("SELECT COUNT(*) AS total FROM orders")
        assert result["error"] is None
        assert result["row_count"] == 1
        assert result["columns"] == ["total"]
        assert result["rows"][0][0] >= 3000

    def test_select_with_limit(self):
        result = execute_raw_sql("SELECT * FROM customers LIMIT 5")
        assert result["error"] is None
        assert result["row_count"] == 5

    def test_aggregation(self):
        result = execute_raw_sql(
            "SELECT status, COUNT(*) AS cnt FROM orders GROUP BY status ORDER BY cnt DESC"
        )
        assert result["error"] is None
        assert result["row_count"] > 1
        statuses = [r[0] for r in result["rows"]]
        assert "completed" in statuses

    def test_join_query(self):
        result = execute_raw_sql("""
            SELECT c.name, SUM(o.total_amount) AS revenue
            FROM orders o
            JOIN customers c ON c.customer_id = o.customer_id
            WHERE o.status = 'completed'
            GROUP BY c.customer_id, c.name
            ORDER BY revenue DESC
            LIMIT 5
        """)
        assert result["error"] is None
        assert result["row_count"] == 5
        assert "revenue" in result["columns"]

    def test_rejects_destructive_sql(self):
        result = execute_raw_sql("DROP TABLE orders")
        assert result["error"] is not None

    def test_invalid_sql_returns_error(self):
        result = execute_raw_sql("SELECT * FROM nonexistent_table_xyz")
        assert result["error"] is not None

    def test_date_filter(self):
        result = execute_raw_sql(
            "SELECT COUNT(*) AS cnt FROM orders WHERE strftime('%Y', order_date) = '2023'"
        )
        assert result["error"] is None
        assert result["rows"][0][0] > 0


# ── Chart Service Tests ──────────────────────────────────────────────────────

class TestChartService:

    def test_bar_chart_for_category_numeric(self):
        df = pd.DataFrame({
            "category": ["Electronics", "Software", "Office"],
            "total_revenue": [50000.0, 30000.0, 20000.0],
        })
        chart = suggest_chart(df)
        assert chart is not None
        assert chart["type"] == "bar"
        assert len(chart["data"]) == 1

    def test_line_chart_for_date_series(self):
        df = pd.DataFrame({
            "order_month": ["2023-01", "2023-02", "2023-03", "2023-04"],
            "total_revenue": [10000.0, 12000.0, 9000.0, 15000.0],
        })
        chart = suggest_chart(df)
        assert chart is not None
        assert chart["type"] == "line"

    def test_no_chart_for_single_column(self):
        df = pd.DataFrame({"name": ["Alice", "Bob"]})
        chart = suggest_chart(df)
        assert chart is None

    def test_no_chart_for_empty_df(self):
        df = pd.DataFrame()
        chart = suggest_chart(df)
        assert chart is None

    def test_scatter_for_two_numeric(self):
        df = pd.DataFrame({
            "unit_price": [100.0, 200.0, 300.0],
            "quantity": [5.0, 3.0, 8.0],
        })
        chart = suggest_chart(df)
        assert chart is not None
        assert chart["type"] == "scatter"

    def test_chart_has_layout(self):
        df = pd.DataFrame({
            "category": ["A", "B", "C"],
            "value": [1.0, 2.0, 3.0],
        })
        chart = suggest_chart(df)
        assert "layout" in chart
        assert "data" in chart


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
