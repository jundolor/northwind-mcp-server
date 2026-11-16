from server_core import mcp
from db import _query, DEFAULT_LIMIT, paged

# === SUPPLIERS ===

@mcp.tool()
def list_suppliers(supplier:str | None = None, limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict:
    """List Suppliers (Supplier Name, Contact Name, City, Address, Country).  
    Returns up to `limit` rows (max 100); if has_more is true, call again with a larger offset.
    Optionally filter by part of the supplier name.
    For full supplier info, use get_supplier."""
    where, params = "", ()
    if supplier:
        where, params = " WHERE SupplierName LIKE ? COLLATE NOCASE", (f"%{supplier}%",)
    return paged(
        "SELECT SupplierName AS [Supplier Name], ContactName AS [Contact Name],"
        f" City, Address, Country FROM Suppliers {where} ORDER BY SupplierName",
        f"SELECT COUNT(*) AS n FROM Suppliers {where}",
        params,
        limit, offset,
        "suppliers")
    

@mcp.tool()
def list_suppliers_by_city(city: str, limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict:
    """List suppliers in a city (exact city name, not case-sensitive). 
    Returns up to `limit` rows (max 100); if has_more is true, call again with a larger  offset. 
    For full supplier info use get_supplier."""
    where = "WHERE City = ? COLLATE NOCASE"
    return paged(
        f"SELECT City, Address, Country, SupplierName AS [Supplier Name], ContactName AS [Contact Name] FROM Suppliers {where} "
        "ORDER BY SupplierName",
        f"SELECT COUNT(*) AS n FROM Suppliers {where}",
        (city,),
        limit, offset,
        "suppliers")
    

@mcp.tool()
def list_suppliers_by_products(product: str | None = None, limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict:
    """List products with their supplier (Product Name, Unit, Price, Supplier Name, City, Country), sorted by supplier. 
    Optionally filter by part of the product name. 
    Returns up to `limit` rows (max 100); if has_more is true, call again with a larger offset. 
    For full supplier info use get_supplier."""
    joins = "FROM Products p JOIN Suppliers s ON s.SupplierID = p.SupplierID"
    where, params = "", ()
    if product:
        where, params = "WHERE p.ProductName LIKE ? COLLATE NOCASE", (f"%{product}%",)
    return paged(
        "SELECT p.ProductName AS [Product Name], p.Unit, p.Price, "
        "s.SupplierName AS [Supplier Name], s.City, s.Country "
        f"{joins} {where} "
        "ORDER BY s.SupplierName, p.ProductName, p.ProductID",
        f"SELECT COUNT(*) AS n {joins} {where}",
        params,
        limit, offset,
        "products")

  
@mcp.tool()
def get_supplier(supplier: str) -> dict:
    """Searches a supplier using supplier name (Supplier Name, Contact Name, City, Address, PostalCode, Country, Phone) 
    """
    rows = _query(
        "SELECT SupplierName AS [Supplier Name], ContactName AS [Contact Name], City, Address, PostalCode, Country, Phone FROM Suppliers"
        " WHERE SupplierName = ? COLLATE NOCASE"
        , (supplier, )
    )

    if not rows:
        return {"msg": f"No supplier found for {supplier!r}. Use list_suppliers for supplier names. Call again with adjusted value."}
    
    return rows[0]

    
