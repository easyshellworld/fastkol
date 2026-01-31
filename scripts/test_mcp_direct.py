from mcp.server.fastmcp import FastMCP
import uvicorn
import asyncio
import httpx

# Create minimal server
mcp = FastMCP("test-server")

@mcp.tool()
def echo(text: str) -> str:
    return f"Echo: {text}"

async def test_connection():
    # Wait for server to start
    await asyncio.sleep(2)
    async with httpx.AsyncClient() as client:
        try:
            # FastMCP defaults to exposing SSE at /sse
            resp = await client.get("http://127.0.0.1:9999/sse")
            print(f"Test 9999/sse: {resp.status_code}")
            print(f"Content: {resp.text[:100]}")
        except Exception as e:
            print(f"Connection failed: {e}")

if __name__ == "__main__":
    # We will run this in a thread or just let uvicorn block and test separately?
    # Better to just run uvicorn and let user see if it binds.
    print("Starting test server on 9999...")
    mcp.run(transport="sse", port=9999)
