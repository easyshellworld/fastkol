import os
from dotenv import load_dotenv

load_dotenv()

from heygen_mcp.server import mcp  # noqa: E402

if __name__ == "__main__":
    host = os.getenv("HEYGEN_MCP_HOST", "127.0.0.1")
    port = int(os.getenv("HEYGEN_MCP_PORT", "7012"))
    mcp.settings.host = host
    mcp.settings.port = port
    mcp.run(transport="streamable-http")
