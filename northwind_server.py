from mcp.server.mcpserver import MCPServer
from pathlib import Path
import sqlite3
import os
from mcp.server.transport_security import TransportSecuritySettings

INSTRUCTIONS = (
    "Read-only access to the Northwind sample database (fictional customers, "
    "suppliers, products and orders). Use list_* tools to browse and get_* tools "
    "to fetch one record. List tools return at most 100 rows per call; "
)

mcp = MCPServer("Northwind MCP Server", instructions=INSTRUCTIONS)
DB_PATH  = Path(__file__).parent/ "northwind.db"
MAX_LIMIT = 100
ABOUT = """\
Northwind MCP Server (read-only)

Data: the Northwind sample database, a fictional trading company with
orders dated 1996-1998. It is sample data, not a real business.
Tools: list_* tools browse records, get_* tools return one record.
Limits: list tools cap results (default 50, maximum 100) and support paging.
Attribution: Northwind sample data originally by Microsoft; see the
repository README for the source and license.
"""


#apply pagination
def _page(limit: int, offset: int) -> tuple[int, int]:
    return max(1, min(limit, MAX_LIMIT)), max(0, offset)

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

# === CATEGORIES ===        

@mcp.tool()
def list_categories(category: str | None = None) -> list[dict]:
    """List Northwind Categories 
    Optionally filter by category, e.g. 'Beverages'.
    Returns Category Name, Description
    """
    if category:
        return _query("SELECT CategoryName AS [Category Name], Description FROM Categories WHERE CategoryName = ? COLLATE NOCASE ORDER BY CategoryName", (category,))
    
    return _query("SELECT CategoryName AS [Category Name], Description FROM Categories ORDER BY CategoryName")

# === CUSTOMERS ===

@mcp.tool()
def list_customer_contacts(query: str) -> list[dict]:
    """Search Customer contacts based on part of name.
    For full customer info use get_customer.
    Returns Contact Name, Customer Name
    """
    p = f"%{query}%"
    return _query("SELECT ContactName AS [Contact Name], CustomerName AS [Customer Name] FROM Customers WHERE ContactName LIKE ? ORDER BY ContactName", (p,))

@mcp.tool()
def list_customers(customer: str | None = None) -> list[dict]:
    """List Customers
    Optionally filter by customer name. For full customer info use get_customer.
    Returns Customer Name, Contact Name, City, Country
    """
    if customer:
        p = f"%{customer}%"
        return _query("SELECT CustomerName AS [Customer Name], ContactName AS [Contact Name], City, Country FROM Customers WHERE CustomerName LIKE ? ORDER BY CustomerName", (p,))

    return _query("SELECT CustomerName AS [Customer Name], ContactName AS [Contact Name], City, Country FROM Customers ORDER BY CustomerName")

@mcp.tool()
def get_customer(name: str) -> dict:
    """Look up a single Northwind customer using the exact customer name.
    Returns Customer Name, Contact Name, Address, City, PostalCode, Country.
    """
    rows = _query(
        "SELECT CustomerName AS [Customer Name], ContactName AS [Contact Name], Address, City, PostalCode, Country"
        " FROM Customers WHERE CustomerName = ? COLLATE NOCASE"
        , (name, )
        )
    if not rows:
        return {"error": f"No Customer found for {name!r}. "
            "Use list_customers to find valid customer names."
        }
    return rows[0]

# === PRODUCTS ===

@mcp.tool()
def list_products(product:str | None=None) -> list[dict]:
    """List Products
    Optionally filter by product name. For full product info use get_product.
    Returns Product Name, Unit (SKU), Price
    """
    if product:
        p = f"%{product}%"
        return _query("SELECT ProductName AS [Product Name], Unit, Price FROM Products WHERE ProductName LIKE ? ORDER BY ProductName", (p,))

    return _query("SELECT ProductName AS [Product Name], Unit, Price FROM Products ORDER BY ProductName")

@mcp.tool()
def get_product(name: str) -> dict:
    """Look up a single Northwind product using the exact product name.
    Returns the Product ID, Product Name, Supplier Name, Category Name, Unit (SKU), Price"""
    if name:
        rows = _query(
                "SELECT p.ProductID AS [Product ID], p.ProductName AS [Product Name],"
                " s.SupplierName AS [Supplier Name], c.CategoryName AS [Category Name],"
                " p.Unit, p.Price"
                " FROM Products p"
                " LEFT JOIN Suppliers s ON p.SupplierID = s.SupplierID"
                " LEFT JOIN Categories c on p.CategoryID = c.CategoryID"
                " WHERE p.ProductName = ? COLLATE NOCASE"
                , (name, )
        )
        if not rows:
            return {"error": f"No product found for {name!r}. "
                "Use list_products to find valid product names."
            }
        return rows[0]
    return {"error":"No product name entered"}

# === SHIPPERS ===

@mcp.tool()
def list_shippers(shipper:str | None=None) -> list[dict]:
    """List Shippers
    Optionally filter by part of shipper name. For full shipper info use get_shipper.
    Returns Shipper Name, Phone
    """
    if shipper:
        p = f"%{shipper}%"
        return _query(
            "SELECT ShipperName AS [Shipper Name], Phone FROM Shippers"
            " WHERE ShipperName LIKE ? COLLATE NOCASE"
            , (p,)
        )

    return _query("SELECT ShipperName AS [Shipper Name], Phone FROM Shippers")

@mcp.tool()
def get_shipper(name: str) -> dict:
    """Look up a single Northwind shipper using the exact shipper name.
    Returns Shipper Name, Phone"""
    if name:
        rows = _query("SELECT ShipperName AS [Shipper Name], Phone FROM Shippers WHERE ShipperName = ? COLLATE NOCASE", (name, ))
        if not rows:
            return {"error": f"No shipper found for {name!r}. Use list_shippers to find valid shipper name"}
        
        return rows[0]

    return {"error: No Shipper name entered"}

# === SUPPLIERS ===

@mcp.tool()
def list_suppliers(supplier: str | None = None) -> list[dict]:
    """List Suppliers
    Optionally filter by part of supplier name. For full supplier info use get_supplier.
    Returns Supplier Name, Contact Name, City, Address, Country
    """
    if supplier:
        p = f"%{supplier}%"
        return _query(
            "SELECT SupplierName AS [Supplier Name], ContactName AS [Contact Name], City, Address, Country  FROM Suppliers"
            " WHERE SupplierName LIKE ? COLLATE NOCASE"
            , (p,)
        )
    return _query("SELECT SupplierName AS [Supplier Name], ContactName AS [Contact Name], City, Address, Country FROM Suppliers")

@mcp.tool()
def list_suppliers_city(city: str) -> list[dict]:
    """List Suppliers by part of city name. For full supplier info use get_supplier.
    Returns Supplier Name, Contact Name, City, Address, Country
    """
    if city:
        p = f"%{city}%"
        return _query(
            "SELECT SupplierName AS [Supplier Name], ContactName AS [Contact Name], City, Address, Country FROM Suppliers"
            " WHERE City LIKE ? COLLATE NOCASE"
            , (p,)
        )
    return {"error": f"No city name entered. "
            "Use list_suppliers to find valid supplier city."
        }

@mcp.tool()
def list_products_suppliers(name:str | None=None) -> list[dict]:
    """List Suppliers with Products
     Optionally filter by part of supplier name. For full supplier info use get_supplier.
     Returns Supplier Name, Supplier City, Supplier Country, Product Name, Unit (SKU),Price
    """
    if name:
        p = f"%{name}%"
        return _query(
            "SELECT s.SupplierName AS [Supplier Name], s.City, s.Country, p.ProductName AS [Product Name], p.Unit, p.Price"
            " FROM Suppliers s"
            " LEFT JOIN Products p ON s.SupplierID = p.SupplierID"
            " WHERE s.SupplierName LIKE ?"
            " ORDER BY p.ProductName"
            , (p, )
        )

    return _query(
        "SELECT s.SupplierName AS [Supplier Name], s.City, s.Country, p.ProductName AS [Product Name], p.Unit, p.Price"
        " FROM Suppliers s"
        " LEFT JOIN Products p ON s.SupplierID = p.SupplierID"
        " ORDER BY s.SupplierName, p.ProductName"
    )

@mcp.tool()
def get_supplier(name: str) -> dict:
    """Look up a single Northwind supplier using the exact supplier name.
    Returns Supplier Name, Contact Name, City, Address, PostalCode, Country, Phone
    """
    if name:
        rows = _query(
            "SELECT SupplierName AS [Supplier Name], ContactName AS [Contact Name], City, Address, PostalCode, Country, Phone FROM Suppliers"
            " WHERE SupplierName = ? COLLATE NOCASE"
            , (name,)
        )
        if not rows:
            return {"error": f"No supplier found for {name!r}. Use list_suppliers to find valid supplier name"}
        
        return rows[0]
    
    return {"error: No Shipper name entered"}

# === ORDERS ===

@mcp.tool()
def list_orders(limit:int = 50, offset:int = 0) -> list[dict]:
    """List Orders. Returns up to `limit` rows (max 100). For order details use get_order_details.
    Returns Order Number, Order Customer, Order Employee, Order Date, Order Shipper
    """
    return _query(
        "SELECT o.OrderID AS [Order Number], c.CustomerName AS [Order Customer], e.LastName || ', ' || e.FirstName AS [Order Employee], o.OrderDate AS [Order Date], sh.ShipperName AS [Order Shipper] " 
        " FROM Orders o"
        " LEFT JOIN Customers c ON o.CustomerID = c.CustomerID"
        " LEFT JOIN Employees e ON o.EmployeeID = e.EmployeeID"
        " LEFT JOIN Shippers sh ON o.ShipperID = sh.ShipperID"
        " LIMIT ? OFFSET ?"
        , (limit, offset)
    )


@mcp.tool()
def list_orders_customers(customer: str | None = None, limit:int = 50, offset:int = 0) -> list[dict]:
    """List Orders by customer name. Returns up to `limit` rows (max 100). For order details use get_order_details.
    Optionally filter by part of customer name
    Returns Order Number, Order Customer, Order Employee, Order Date, Order Shipper
    """
    limit, offset = _page(limit, offset)
    query_str = "SELECT o.OrderID AS [Order Number], c.CustomerName AS [Order Customer], e.LastName || ', ' || e.FirstName AS [Order Employee], o.OrderDate AS [Order Date], sh.ShipperName AS [Order Shipper] " 
    query_str += " FROM Orders o"
    query_str += " LEFT JOIN Customers c ON o.CustomerID = c.CustomerID"
    query_str += " LEFT JOIN Employees e ON o.EmployeeID = e.EmployeeID"
    query_str += " LEFT JOIN Shippers sh ON o.ShipperID = sh.ShipperID"
    if customer:
        query_str += " WHERE c.CustomerName = ?"
        params = (customer, limit, offset,)
    else:
        params = (limit, offset,)
    query_str += " LIMIT ? OFFSET ?"
    
    return _query(query_str, params)

@mcp.tool()
def get_order_details(order_number: int) -> list[dict]:
    """List order details using the order number.
    Returns Order Number, ProductName, Quantity
    """
    if order_number:
        return _query(
            "SELECT od.OrderID AS [Order Number], p.ProductName, od.Quantity"
            " FROM OrderDetails od"
            " LEFT JOIN Products p on od.ProductID = p.ProductID"
            " WHERE od.OrderID = ?"
            , (order_number, )
        )

    return {"error: No Order number entered"}

@mcp.tool()
def list_product_orders(product:str | None=None,  limit:int = 50, offset:int = 0) -> list[dict]:
    """List Orders by exact product name. Returns up to `limit` rows (max 100). For order details use get_order_details.
    Optionally filter by part of product name
    Returns Product Name, Order Number, Order Date, Customer, Order Quantity
    """
    query_str = "SELECT p.ProductName AS [Product Name], o.OrderID AS [Order Number], OrderDate AS [Order Date], CustomerName AS [Customer], od.Quantity AS [Order Quantity]"
    query_str += " FROM Products p"
    query_str += " LEFT JOIN OrderDetails od on p.ProductID = od.ProductID"
    query_str += " JOIN Orders o on od.OrderID = o.OrderID "
    query_str += " JOIN Customers c on o.CustomerID = c.CustomerID"

    if product:
        query_str += " WHERE p.ProductName = ?"
        params = (product, limit, offset)
    else:
        params = (limit, offset)

    query_str += " LIMIT ? OFFSET ?"

    return _query(query_str, params)

@mcp.resource("greeting://{name}")
def greeting(name: str) ->str:
    """Greet and orient consumer"""
    return f"Hello {name}, welcome to the Northwind MCP Server. This provides list of tools available to get information from Northwind."

@mcp.resource("northwind://about")
def about()->str:
    """Overview of the Northwind data, the available tools, limits and attribution."""
    return ABOUT

# --- Deployment: an ASGI app, only built when ALLOWED_HOSTS is set -------------
_hosts = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
if _hosts:
    security = TransportSecuritySettings(
        allowed_hosts=[*_hosts, *(f"{h}:*" for h in _hosts)]
    )
    app = mcp.streamable_http_app(transport_security=security)

if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "http":
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run() #run to stdio