from mcp.server.mcpserver import MCPServer

INSTRUCTIONS = (
    "Read-only access to the Northwind sample database (fictional customers, "
    "suppliers, products and orders). Use list_* tools to browse and get_* tools "
    "to fetch one record. List tools return at most 100 rows per call. If has_more is true, "
    "call again with a larger offset."
)

mcp = MCPServer("Northwind MCP Server", instructions=INSTRUCTIONS)