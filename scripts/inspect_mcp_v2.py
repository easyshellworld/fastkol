import sys
from heygen_mcp.server import mcp

print(f"MCP Type: {type(mcp)}")
print("Attributes:")
for d in dir(mcp):
    print(d)
