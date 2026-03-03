"""
SQLite connection management and schema introspection.
All queries run in read-only mode against the analyst database.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from app.core.config import settings


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Yield a read-only SQLite connection."""
    conn = sqlite3.connect(f"file:{settings.DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    try:
        yield conn
    finally:
        conn.close()


def get_schema() -> dict[str, list[dict]]:
    """
    Return full schema: {table_name: [{name, type, pk, notnull, default}]}.
    Used to build the prompt context for Claude.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]

        schema = {}
        for table in tables:
            cur.execute(f"PRAGMA table_info({table})")
            cols = []
            for row in cur.fetchall():
                cols.append({
                    "name": row["name"],
                    "type": row["type"],
                    "pk": bool(row["pk"]),
                    "notnull": bool(row["notnull"]),
                    "default": row["dflt_value"],
                })
            schema[table] = cols
        return schema


def get_schema_as_text() -> str:
    """
    Render schema as SQL CREATE TABLE statements.
    This is passed to Claude as context.
    """
    schema = get_schema()
    lines = []
    for table, cols in schema.items():
        col_defs = []
        for c in cols:
            defn = f"  {c['name']} {c['type']}"
            if c["pk"]:
                defn += " PRIMARY KEY"
            if c["notnull"] and not c["pk"]:
                defn += " NOT NULL"
            if c["default"] is not None:
                defn += f" DEFAULT {c['default']}"
            col_defs.append(defn)
        lines.append(f"CREATE TABLE {table} (\n" + ",\n".join(col_defs) + "\n);")
    return "\n\n".join(lines)


def get_sample_values() -> dict[str, dict[str, list]]:
    """
    Return a few sample values per column for key columns.
    Helps Claude understand the data range and format.
    """
    samples = {}
    key_columns = {
        "customers": ["segment", "country"],
        "products": ["category"],
        "orders": ["status"],
        "sales_reps": ["region"],
    }
    with get_connection() as conn:
        cur = conn.cursor()
        for table, cols in key_columns.items():
            samples[table] = {}
            for col in cols:
                try:
                    cur.execute(f"SELECT DISTINCT {col} FROM {table} LIMIT 10")
                    samples[table][col] = [row[0] for row in cur.fetchall() if row[0]]
                except Exception:
                    pass
    return samples


def get_row_counts() -> dict[str, int]:
    """Return row count per table."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        counts = {}
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cur.fetchone()[0]
        return counts
