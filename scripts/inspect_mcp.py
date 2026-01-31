import sys
try:
    from heygen_mcp.server import mcp
    print(f"Type: {type(mcp)}")
    print(f"Dir: {dir(mcp)}")
    if hasattr(mcp, 'settings'):
        print(f"Settings: {mcp.settings}")
    if hasattr(mcp, '_sse_app'):
        print("Has _sse_app (ASGI compliant)")
except ImportError:
    print("Could not import heygen_mcp.server")
except Exception as e:
    print(f"Error: {e}")
