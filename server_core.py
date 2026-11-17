from mcp.server.mcpserver import MCPServer

INSTRUCTIONS = (
    "Read-only access to the Northwind sample database (fictional customers, "
    "suppliers, products and orders). Use list_* tools to browse and get_* tools "
    "to fetch one record. List tools return 20 rows by default and at most 100 "
    "per call, with a total count. If has_more is true, call again with offset "
    "increased by the number of rows returned."
)

mcp = MCPServer("Northwind MCP Server", instructions=INSTRUCTIONS)