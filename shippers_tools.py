from server_core import mcp
from db import _query, DEFAULT_LIMIT, paged

# === SHIPPERS ===

@mcp.tool()
def list_shippers(limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict:
    """List shippers (Shipper Name, Phone), sorted by shipper name. Returns up
    to `limit` rows (max 100); if has_more is true, call again with a larger
    offset. For full shipper info use get_shipper."""
    return paged(
        "SELECT ShipperName AS [Shipper Name], Phone FROM Shippers "
        "ORDER BY ShipperName",
        "SELECT COUNT(*) AS n FROM Shippers",
        (),
        limit, offset,
        "shippers")


@mcp.tool()
def get_shipper(shipper: str) -> dict:
    """Searches up a shipper using the shipper name.
    Returns Shipper Name, Phone"""
    rows = _query("SELECT ShipperName AS [Shipper Name], Phone FROM Shippers WHERE ShipperName = ? COLLATE NOCASE", (shipper, ))

    if not rows:
        return {"msg": f"No shipper found for {shipper!r}. Use list_shippers for shipper names. Call again with adjusted value."}

    return rows[0]
