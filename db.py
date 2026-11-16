import sqlite3
from pathlib import Path

DB_PATH  = Path(__file__).parent/ "northwind.db"
DEFAULT_LIMIT = 20
MAX_LIMIT = 100

def _query(sql: str, params: tuple = ()) -> list[dict]:
    if not DB_PATH.exists():
        raise ValueError("Database not found.")
    # mode=ro opens the database read-only, so these tools can't change data
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()

def paged(select_sql, count_sql, params, limit, offset, key):
    """Run a query one page at a time and say whether more rows exist."""
    limit = max(1, min(limit, MAX_LIMIT))
    offset = max(0, offset)
    total = _query(count_sql, params)[0]["n"]
    rows = _query(select_sql + " LIMIT ? OFFSET ?", params + (limit, offset))
    return {"total": total, "offset": offset, "returned": len(rows),
            "has_more": offset + len(rows) < total, key: rows}