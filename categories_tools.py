from server_core import mcp
from db import DEFAULT_LIMIT, paged

# === CATEGORIES ===        

@mcp.tool()
def list_categories(category: str | None = None, limit:int = DEFAULT_LIMIT, offset:int = 0) -> dict:
    """List Categories. Returns up to `limit` rows (max 100). 
    Returns up to `limit` rows (max 100); if has_more is true, call again with a larger  offset. 
    Optionally filter by part of category name.
    Returns Category Name, Description
    """
    where, params = "", ()
    if category:
        where, params = " WHERE CategoryName LIKE ? COLLATE NOCASE", (f"%{category}%",)
    return paged(
        f"SELECT CategoryName AS [Category Name], Description FROM Categories {where} ORDER BY CategoryName",
        f"SELECT COUNT(*) AS n FROM Categories {where}",
        params,
        limit,
        offset,
        "categories"
    )