"""
Chart configuration generator.
Takes a pandas DataFrame and a hint about the query intent,
then returns a Plotly-compatible chart spec (JSON-serialisable dict).
"""
import pandas as pd
from typing import Optional


def _is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def _is_date_like(col_name: str) -> bool:
    return any(k in col_name.lower() for k in ["date", "month", "year", "week", "quarter", "period"])


def suggest_chart(
    df: pd.DataFrame,
    query_hint: str = "",
) -> Optional[dict]:
    """
    Analyse the DataFrame shape and column names to suggest the best chart type.
    Returns a Plotly figure dict, or None if no chart is appropriate.
    """
    if df.empty or len(df.columns) < 2:
        return None

    if len(df) > 200:
        df = df.head(200)

    cols = list(df.columns)
    numeric_cols = [c for c in cols if _is_numeric(df[c])]
    non_numeric_cols = [c for c in cols if not _is_numeric(df[c])]
    date_cols = [c for c in cols if _is_date_like(c)]

    hint = query_hint.lower()

    # ── Time series ──────────────────────────────────────────────────────────
    if date_cols and numeric_cols:
        x_col = date_cols[0]
        y_col = numeric_cols[0]
        df_sorted = df.sort_values(x_col)
        return {
            "type": "line",
            "data": [
                {
                    "x": df_sorted[x_col].astype(str).tolist(),
                    "y": df_sorted[y_col].tolist(),
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": _label(y_col),
                    "line": {"color": "#f59e0b", "width": 2},
                    "marker": {"size": 5, "color": "#f59e0b"},
                }
            ],
            "layout": _layout(f"{_label(y_col)} over {_label(x_col)}", x_col, y_col),
        }

    # ── Category + numeric: bar chart ────────────────────────────────────────
    if non_numeric_cols and numeric_cols:
        x_col = non_numeric_cols[0]
        y_col = numeric_cols[0]

        # Limit to top 20 for readability
        df_plot = df[[x_col, y_col]].dropna()
        if len(df_plot) > 20:
            df_plot = df_plot.nlargest(20, y_col)
        df_plot = df_plot.sort_values(y_col, ascending=False)

        orientation = "h" if len(df_plot) > 10 else "v"

        if orientation == "h":
            trace = {
                "y": df_plot[x_col].astype(str).tolist(),
                "x": df_plot[y_col].tolist(),
                "type": "bar",
                "orientation": "h",
                "name": _label(y_col),
                "marker": {"color": "#f59e0b"},
            }
            layout = _layout(f"{_label(y_col)} by {_label(x_col)}", y_col, x_col)
            layout["yaxis"]["autorange"] = "reversed"
        else:
            trace = {
                "x": df_plot[x_col].astype(str).tolist(),
                "y": df_plot[y_col].tolist(),
                "type": "bar",
                "name": _label(y_col),
                "marker": {"color": "#f59e0b"},
            }
            layout = _layout(f"{_label(y_col)} by {_label(x_col)}", x_col, y_col)

        return {"type": "bar", "data": [trace], "layout": layout}

    # ── Two numeric columns: scatter ─────────────────────────────────────────
    if len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        label_col = non_numeric_cols[0] if non_numeric_cols else None
        trace = {
            "x": df[x_col].tolist(),
            "y": df[y_col].tolist(),
            "type": "scatter",
            "mode": "markers",
            "marker": {"color": "#f59e0b", "size": 8, "opacity": 0.7},
            "name": f"{_label(x_col)} vs {_label(y_col)}",
        }
        if label_col:
            trace["text"] = df[label_col].astype(str).tolist()
            trace["hovertemplate"] = "%{text}<br>%{x}<br>%{y}<extra></extra>"

        return {
            "type": "scatter",
            "data": [trace],
            "layout": _layout(f"{_label(x_col)} vs {_label(y_col)}", x_col, y_col),
        }

    return None


def _label(col: str) -> str:
    """Convert snake_case to Title Case label."""
    return col.replace("_", " ").title()


def _layout(title: str, x_col: str = "", y_col: str = "") -> dict:
    """Standard dark-themed Plotly layout."""
    return {
        "title": {"text": title, "font": {"color": "#f1f5f9", "size": 14, "family": "IBM Plex Mono"}},
        "paper_bgcolor": "#0f1319",
        "plot_bgcolor": "#0f1319",
        "font": {"color": "#94a3b8", "family": "IBM Plex Mono"},
        "xaxis": {
            "title": _label(x_col),
            "gridcolor": "#1e293b",
            "linecolor": "#1e293b",
            "tickfont": {"color": "#64748b"},
        },
        "yaxis": {
            "title": _label(y_col),
            "gridcolor": "#1e293b",
            "linecolor": "#1e293b",
            "tickfont": {"color": "#64748b"},
        },
        "margin": {"t": 50, "b": 50, "l": 60, "r": 20},
        "showlegend": False,
        "hoverlabel": {
            "bgcolor": "#1e293b",
            "bordercolor": "#334155",
            "font": {"color": "#f1f5f9"},
        },
    }
