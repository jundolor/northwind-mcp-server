from server_core import mcp
from db import _query, DEFAULT_LIMIT, paged

# === PRODUCTS ===
@mcp.tool()
def list_products(product: str | None = None, limit: int = DEFAULT_LIMIT,  offset: int = 0) -> dict:
    """List products (Product Name, Unit, Price), sorted by product name.
    Optionally filter by part of the product name. Returns up to `limit` rows
    (max 100); if has_more is true, call again with a larger offset. For full
    product info, use get_product."""
    where, params = "", ()
    if product:
        where, params = "WHERE ProductName LIKE ? COLLATE NOCASE", (f"%{product}%",)
    return paged(
        "SELECT ProductName AS [Product Name], Unit, Price FROM Products "
        f"{where} ORDER BY ProductName, ProductID",
        f"SELECT COUNT(*) AS n FROM Products {where}",
        params,
        limit, offset,
        "products")


@mcp.tool()
def list_products_by_orders_count(product: str | None = None, limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict:
    """List products with the number of order lines they appear in (Product Name, No of Orders), sorted by product name. 
    Optionally filter by part of the product name. 
    Returns up to `limit` rows (max 100); if has_more is true, call again with a larger offset. 
    For full product info use get_product."""
    joins = "FROM Products p LEFT JOIN OrderDetails od ON p.ProductID = od.ProductID"
    group = "GROUP BY p.ProductID, p.ProductName"
    where, params = "", ()
    if product:
        where, params = "WHERE p.ProductName LIKE ? COLLATE NOCASE", (f"%{product}%",)
    return paged(
        "SELECT p.ProductName AS [Product Name], "
        "COUNT(od.OrderDetailID) AS [No of Orders] "
        f"{joins} {where} {group} ORDER BY p.ProductName, p.ProductID",
        f"SELECT COUNT(*) AS n FROM (SELECT p.ProductID {joins} {where} {group})",
        params,
        limit, offset,
        "products")


@mcp.tool()
def list_products_by_orders_details(product:str | None=None, limit:int = DEFAULT_LIMIT, offset:int = 0) -> dict:
    """List Products by order details.
    Optionally filter by part of the product name.
    For full product info use get_product.
    Returns Product Name, Orders No, Quantity
    """
    line_joins = (
        "FROM Products p"
        " LEFT JOIN OrderDetails od ON p.ProductID = od.ProductID"
        " JOIN Orders o on od.OrderID = o.OrderID "
        " JOIN Customers c on o.CustomerID = c.CustomerID"
    )
    where, params = "", ()
    if product:
        where, params = " WHERE p.ProductName LIKE ? COLLATE NOCASE", (f"%{product}%", )
    return paged(
        "SELECT p.ProductName AS [Product Name], od.OrderID AS [Order No], o.OrderDate AS [Order Date], c.CustomerName AS [Order Customer], od.Quantity"
        f" {line_joins} {where}"
        " ORDER BY p.ProductName",
        f"SELECT COUNT(*) AS n {line_joins} {where}",
        params,
        limit, offset,
        "products"
    )


@mcp.tool()
def get_product(product: str) -> dict:
    """Look up a single Northwind product using the  product name.
    Returns the Product ID, Product Name, Supplier Name, Category Name, Unit (SKU), Price"""
    rows = _query(
            "SELECT p.ProductID AS [Product ID], p.ProductName AS [Product Name],"
            " s.SupplierName AS [Supplier Name], c.CategoryName AS [Category Name],"
            " p.Unit, p.Price"
            " FROM Products p"
            " LEFT JOIN Suppliers s ON p.SupplierID = s.SupplierID"
            " LEFT JOIN Categories c on p.CategoryID = c.CategoryID"
            " WHERE p.ProductName = ? COLLATE NOCASE"
            , (product,)
    )

    if not rows:
        return [{"msg": f"Zero rows for {product!r}. Use list_products for product names. Call again with adjusted values."}]

    return rows[0]
