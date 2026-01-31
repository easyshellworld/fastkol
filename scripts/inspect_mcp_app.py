
from heygen_mcp.server import mcp
import inspect

print(f"Type of mcp.sse_app: {type(mcp.sse_app)}")
print(f"Is callable? {callable(mcp.sse_app)}")
if callable(mcp.sse_app):
    print(f"Signature: {inspect.signature(mcp.sse_app)}")
