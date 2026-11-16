from server_core import mcp
from db import _query, DEFAULT_LIMIT, paged

# === CUSTOMERS ===

@mcp.tool()
def list_customers(customer: str | None = None, limit:int = DEFAULT_LIMIT, offset:int = 0) -> dict:
    """List Customers (Customer Name, Contact Name, City, Address, Country).  
        Returns up to `limit` rows (max 100); if has_more is true, call again with a larger offset.
        Optionally filter by part of the customer name.
        For full customer info, use get_customer."""
    where, params = "", ()
    if customer:
        where, params = " WHERE CustomerName LIKE ?", (f"%{customer}%",)

    return paged(
        "SELECT CustomerName AS [Customer Name], ContactName AS [Contact Name], City, Country FROM Customers"
        f" {where}"
        " ORDER BY CustomerName",
        f"SELECT COUNT(*) AS n FROM Customers {where}",
        params,
        limit,
        offset,
        "customers"
    )
    

@mcp.tool()
def list_customer_by_contacts(contact: str , limit:int = DEFAULT_LIMIT, offset:int = 0) -> dict:
    """List Customers using part of contact name (Customer Name, Contact Name, City, Address, Country).  
    Returns up to `limit` rows (max 100); if has_more is true, call again with a larger offset.
    For full customer info, use get_customer."""
    where, params = " WHERE ContactName LIKE ?", (f"%{contact}%",)
    return paged(
        f"SELECT ContactName AS [Contact Name], CustomerName AS [Customer Name] FROM Customers {where} ORDER BY ContactName",
        f"SELECT COUNT(*) AS n FROM Customers {where}",
        params,
        limit,
        offset,
        "customers"
    )


@mcp.tool()
def list_customers_by_orders_count(customer: str | None = None, limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict:
    """List Number of Orders by Customer (Customer Name, No. of Orders). 
    Returns up to `limit` rows (max 100); if has_more is true, call again with a larger offset.
    Optionally filter by customer name. In this case, limit and offset will not apply"""
    joins = " FROM Customers c LEFT JOIN Orders o ON c.CustomerID = o.CustomerID"
    group = " GROUP BY c.CustomerName"
    where, params = "", ()
    if customer:
        where, params = " WHERE c.CustomerName = ? COLLATE NOCASE", (customer,)
    return paged(
        "SELECT c.CustomerName AS [Customer Name], COUNT(o.OrderID) AS [No of Orders]"
        f"{joins} {where} {group}",
        f"SELECT COUNT(*) AS n FROM (SELECT c.CustomerName {joins} {where} {group})",
        params,
        limit,
        offset,
        "customers"
    )
    

@mcp.tool()
def list_customers_by_orders_details(customer: str | None = None, limit:int = DEFAULT_LIMIT, offset:int = 0) -> dict:
    """List Orders by Customer Name (Customer Name, Order No, Order Employee, Order Date, Order Shipper). 
    Returns up to `limit` rows (max 100); if has_more is true, call again with a larger offset.
    Optionally filter by customer name
    For order details use get_order_details."""
    line_joins = (
        " FROM Orders o"
        " LEFT JOIN Customers c ON o.CustomerID = c.CustomerID"
        " LEFT JOIN Employees e ON o.EmployeeID = e.EmployeeID"
        " LEFT JOIN Shippers sh ON o.ShipperID = sh.ShipperID"
    )
    where, params = "", ()
    if customer:
        where, params = " WHERE c.CustomerName = ? COLLATE NOCASE", (customer,)
    return paged(
         "SELECT c.CustomerName AS [Customer Name], o.OrderID AS [Order No], e.LastName || ', ' || e.FirstName AS [Order Employee], o.OrderDate AS [Order Date], sh.ShipperName AS [Order Shipper]" 
         f" {line_joins} {where}"
         " ORDER BY c.CustomerName",
         f"SELECT COUNT(*) AS n {line_joins} {where}",
         params,
         limit,
         offset,
         "customers"
    )


@mcp.tool()
def get_customer(name: str) -> dict:
    """Searhes single customer using the customer name.
    Returns Customer Name, Contact Name, Address, City, PostalCode, Country.
    """
    rows = _query(
        "SELECT CustomerName AS [Customer Name], ContactName AS [Contact Name], Address, City, PostalCode, Country"
        " FROM Customers WHERE CustomerName = ? COLLATE NOCASE"
        , (name, )
        )
    if not rows:
        return {"msg": f"No Customer found for {name!r}. Use list_customers to find valid customer names."}
    
    return rows[0]