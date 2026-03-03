from pydantic import BaseModel, Field
from typing import Optional, Any


class NLQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


class SQLQueryRequest(BaseModel):
    sql: str = Field(..., min_length=5, max_length=5000)


class ChartData(BaseModel):
    type: str
    data: list[dict]
    layout: dict


class QueryResponse(BaseModel):
    sql: str
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    truncated: bool
    chart: Optional[dict]
    execution_ms: int
    error: Optional[str]


class SchemaColumn(BaseModel):
    name: str
    type: str
    pk: bool
    notnull: bool
    default: Optional[str]


class SchemaResponse(BaseModel):
    tables: dict[str, list[dict]]
    row_counts: dict[str, int]


class SuggestionsResponse(BaseModel):
    suggestions: list[str]
