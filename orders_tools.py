from server_core import mcp
from db import _query, DEFAULT_LIMIT, paged

# === ORDERS ===

@mcp.tool()
def list_orders(limit:int = DEFAULT_LIMIT, offset:int = 0) -> dict:
    """List Orders (Order No, Order Customer, Order Employee, Order Date, Order Shipper), sorted by Order No.
       Returns up to `limit` rows  (max 100); if has_more is true, call again with a larger offset. 
       For full order details, use get_order_details"""
    line_joins = (
        " FROM Orders o"
        " LEFT JOIN Customers c ON o.CustomerID = c.CustomerID"
        " LEFT JOIN Employees e ON o.EmployeeID = e.EmployeeID"
        " LEFT JOIN Shippers sh ON o.ShipperID = sh.ShipperID"  
    )
    return paged(
        "SELECT o.OrderID AS [Order No], c.CustomerName AS [Order Customer], e.LastName || ', ' || e.FirstName AS [Order Employee], o.OrderDate AS [Order Date], sh.ShipperName AS [Order Shipper] "
        f" {line_joins} ORDER BY o.OrderID"
        , f"SELECT COUNT(*) AS n {line_joins}"
        , ()
        , limit
        , offset
        , "orders"
    )


@mcp.tool()
def get_order_details(order_number: int) -> list[dict]:
    """Searches Order Details using the Order Number.
    Returns Order Number, ProductName, Quantity
    """
    if order_number:
        rows = _query(
            "SELECT od.OrderID AS [Order Number], p.ProductName, od.Quantity"
            " FROM OrderDetails od"
            " LEFT JOIN Products p on od.ProductID = p.ProductID"
            " WHERE od.OrderID = ?"
            , (order_number, )
        )

    if not rows:
        return [{"msg":f"Zero rows for order number {order_number}. Use list_orders for order numbers. Call again with adjusted values."}]

    return rows
        
