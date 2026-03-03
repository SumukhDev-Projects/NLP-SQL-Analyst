"""
SQL safety layer.
All queries are validated before execution to prevent destructive operations.
Only SELECT statements are permitted.
"""
import re
from typing import Tuple

# These keywords should never appear in a read-only query
FORBIDDEN_KEYWORDS = [
    r"\bDROP\b", r"\bDELETE\b", r"\bINSERT\b", r"\bUPDATE\b",
    r"\bCREATE\b", r"\bALTER\b", r"\bTRUNCATE\b", r"\bREPLACE\b",
    r"\bATTACH\b", r"\bDETACH\b", r"\bPRAGMA\b", r"\bVACUUM\b",
    r"\bANALYZE\b",
]


def validate_sql(sql: str) -> Tuple[bool, str]:
    """
    Returns (is_safe, reason).
    Accepts only SELECT statements with no destructive keywords.
    """
    if not sql or not sql.strip():
        return False, "Empty query."

    cleaned = sql.strip().rstrip(";")
    upper = cleaned.upper()

    # Must start with SELECT (or WITH for CTEs)
    if not re.match(r"^\s*(SELECT|WITH)\b", upper):
        return False, "Only SELECT queries are permitted."

    # Check for forbidden keywords
    for pattern in FORBIDDEN_KEYWORDS:
        if re.search(pattern, upper):
            keyword = pattern.replace(r"\b", "").strip()
            return False, f"Forbidden keyword detected: {keyword}"

    # Reject multiple statements
    # Strip string literals first to avoid false positives
    stripped = re.sub(r"'[^']*'", "''", cleaned)
    stripped = re.sub(r'"[^"]*"', '""', stripped)
    if ";" in stripped:
        return False, "Multiple statements are not allowed."

    return True, "OK"


def clean_sql(sql: str) -> str:
    """Remove markdown code fences and extra whitespace from Claude's response."""
    sql = sql.strip()
    # Remove ```sql ... ``` fences
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql)
    sql = sql.strip().rstrip(";")
    return sql
