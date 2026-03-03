"""
NL-to-SQL translation service using Claude.

Responsibilities:
- Build a rich prompt with schema + sample values
- Call Claude to generate SQL
- Validate and clean the returned SQL
- Execute the query
- Return results + chart suggestion
"""
import pandas as pd
import sqlite3
import time
from typing import Optional

import anthropic

from app.core.config import settings
from app.db.connection import get_connection, get_schema_as_text, get_sample_values
from app.utils.sql_safety import validate_sql, clean_sql
from app.services.chart_service import suggest_chart

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


# ── Prompt construction ───────────────────────────────────────────────────────

def _build_system_prompt(schema_text: str, sample_values: dict) -> str:
    samples_text = []
    for table, cols in sample_values.items():
        for col, vals in cols.items():
            samples_text.append(f"  {table}.{col}: {vals}")

    return f"""You are an expert SQL analyst. Convert natural language questions into correct SQLite SELECT queries.

DATABASE SCHEMA:
{schema_text}

SAMPLE VALUES (to help you understand data formats and valid filter values):
{chr(10).join(samples_text)}

RULES:
1. Output ONLY the raw SQL query — no explanation, no markdown, no backticks, no semicolon at the end.
2. Only use SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, CREATE, or any DDL/DML.
3. All date columns store values as TEXT in format 'YYYY-MM-DD'. Use strftime() or string comparison for date filtering.
4. For aggregations with date, use strftime('%Y-%m', order_date) for monthly, strftime('%Y', order_date) for yearly.
5. Use meaningful column aliases (e.g. SUM(total_amount) AS total_revenue).
6. Always use table aliases in JOINs to avoid ambiguity.
7. Limit results to {settings.MAX_ROWS_RETURNED} rows unless the user asks for a specific number.
8. For "top N" queries, use ORDER BY ... DESC LIMIT N.
9. When calculating profit, use: (unit_price - unit_cost) * quantity from order_items joined with products.
10. The orders table has a 'status' column. Completed orders have status = 'completed'. Exclude 'cancelled' and 'refunded' for revenue unless asked.
11. For percentage calculations, use CAST(numerator AS REAL) / denominator * 100.

Think step by step, then output only the final SQL."""


def _build_user_message(question: str) -> str:
    return f"Question: {question}\n\nSQL:"


# ── Main query function ───────────────────────────────────────────────────────

def run_nl_query(question: str) -> dict:
    """
    Full pipeline: question -> SQL -> execute -> results + chart.

    Returns:
        {
            sql: str,
            columns: list[str],
            rows: list[list],
            row_count: int,
            chart: dict | None,
            execution_ms: int,
            error: str | None,
        }
    """
    start = time.perf_counter()

    # 1. Build prompt context
    schema_text = get_schema_as_text()
    sample_values = get_sample_values()
    system_prompt = _build_system_prompt(schema_text, sample_values)

    # 2. Call Claude
    try:
        response = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=settings.MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": _build_user_message(question)}],
        )
        raw_sql = response.content[0].text.strip()
    except anthropic.APIError as e:
        return _error_result(f"Claude API error: {str(e)}")

    # 3. Clean and validate
    sql = clean_sql(raw_sql)
    is_safe, reason = validate_sql(sql)
    if not is_safe:
        return _error_result(f"Generated SQL failed safety check: {reason}", sql=sql)

    # 4. Execute
    try:
        with get_connection() as conn:
            df = pd.read_sql_query(
                sql,
                conn,
                params=None,
            )
    except sqlite3.OperationalError as e:
        return _error_result(f"SQL execution error: {str(e)}", sql=sql)
    except Exception as e:
        return _error_result(f"Unexpected error: {str(e)}", sql=sql)

    # 5. Truncate if too large
    truncated = False
    if len(df) > settings.MAX_ROWS_RETURNED:
        df = df.head(settings.MAX_ROWS_RETURNED)
        truncated = True

    # 6. Generate chart suggestion
    chart = suggest_chart(df, query_hint=question)

    # 7. Serialize
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    # Convert DataFrame to JSON-safe format
    columns = list(df.columns)
    rows = []
    for _, row in df.iterrows():
        rows.append([
            None if pd.isna(v) else (float(v) if isinstance(v, (int, float)) else str(v))
            for v in row
        ])

    return {
        "sql": sql,
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "truncated": truncated,
        "chart": chart,
        "execution_ms": elapsed_ms,
        "error": None,
    }


def _error_result(message: str, sql: str = "") -> dict:
    return {
        "sql": sql,
        "columns": [],
        "rows": [],
        "row_count": 0,
        "truncated": False,
        "chart": None,
        "execution_ms": 0,
        "error": message,
    }


def execute_raw_sql(sql: str) -> dict:
    """Execute a raw SQL string (from the advanced SQL editor)."""
    start = time.perf_counter()

    sql = clean_sql(sql)
    is_safe, reason = validate_sql(sql)
    if not is_safe:
        return _error_result(reason, sql=sql)

    try:
        with get_connection() as conn:
            df = pd.read_sql_query(sql, conn)
    except Exception as e:
        return _error_result(str(e), sql=sql)

    if len(df) > settings.MAX_ROWS_RETURNED:
        df = df.head(settings.MAX_ROWS_RETURNED)

    chart = suggest_chart(df)
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    columns = list(df.columns)
    rows = [
        [None if pd.isna(v) else (float(v) if isinstance(v, (int, float)) else str(v)) for v in row]
        for _, row in df.iterrows()
    ]

    return {
        "sql": sql,
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "truncated": len(rows) >= settings.MAX_ROWS_RETURNED,
        "chart": chart,
        "execution_ms": elapsed_ms,
        "error": None,
    }
