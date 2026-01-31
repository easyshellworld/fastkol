from mcp.server.fastmcp import FastMCP
mcp = FastMCP("test")
print("Attributes:", dir(mcp))
if hasattr(mcp, 'sse_app'):
    print("Has sse_app")
elif hasattr(mcp, '_sse_app'):
    print("Has _sse_app")
