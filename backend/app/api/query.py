from fastapi import APIRouter, HTTPException

from app.core.schemas import (
    NLQueryRequest, SQLQueryRequest,
    QueryResponse, SchemaResponse, SuggestionsResponse,
)
from app.db.connection import get_schema, get_row_counts
from app.services.query_service import run_nl_query, execute_raw_sql

router = APIRouter()


# ── Sample questions people can click to explore the DB ──────────────────────
SUGGESTIONS = [
    "What are the top 10 customers by total revenue?",
    "Show monthly revenue trend for 2023",
    "Which product categories generate the most revenue?",
    "What is the average order value by customer segment?",
    "Which sales reps exceeded their annual quota?",
    "Show revenue breakdown by country",
    "What are the top 5 products by units sold?",
    "What percentage of orders were cancelled or refunded?",
    "Compare revenue across quarters in 2024",
    "Which region has the highest average order value?",
    "Show the top 10 products by profit margin",
    "How many new customers signed up each month in 2023?",
    "What is the revenue contribution of each customer segment?",
    "Which cities generate the most orders?",
    "Show total discounts given per product category",
]


@router.post("/query", response_model=QueryResponse)
async def nl_query(request: NLQueryRequest):
    """
    Convert a natural language question to SQL, execute it,
    and return the results with an optional chart config.
    """
    result = run_nl_query(request.question)
    if result["error"] and not result["sql"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/sql", response_model=QueryResponse)
async def raw_sql_query(request: SQLQueryRequest):
    """
    Execute a raw SQL query directly (read-only, SELECT only).
    Used by the advanced SQL editor in the frontend.
    """
    result = execute_raw_sql(request.sql)
    if result["error"] and not result["sql"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/schema", response_model=SchemaResponse)
async def get_db_schema():
    """Return full database schema and row counts for the schema explorer."""
    return SchemaResponse(
        tables=get_schema(),
        row_counts=get_row_counts(),
    )


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions():
    """Return sample questions for the frontend suggestion bar."""
    return SuggestionsResponse(suggestions=SUGGESTIONS)
