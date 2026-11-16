import os
from mcp.server.transport_security import TransportSecuritySettings
from server_core import mcp
import categories_tools
import customers_tools
import orders_tools
import products_tools
import shippers_tools
import suppliers_tools

ABOUT = """\
Northwind MCP Server (read-only)

Data: the Northwind sample database, a fictional trading company with
orders dated 1996-1998. It is sample data, not a real business.
Tools: list_* tools browse records, get_* tools return one record.
Limits: list tools cap results (default 20, maximum 100) and support paging.
Attribution: Northwind sample data originally by Microsoft; see the
repository README for the source and license.
"""

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