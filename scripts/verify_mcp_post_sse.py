import httpx
import asyncio

async def verify_post_sse(port, name):
    url = f"http://127.0.0.1:{port}/sse"
    print(f"\nProbing {name} at {url} (POST)...")
    
    # Mock JSON-RPC payload that Spoon AI might send
    payload = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # We expect the middleware to redirect POST /sse to /messages
            # FastMCP /messages usually returns 202 or similar for accepted messages
            response = await client.post(url, json=payload)
            print(f"Status Code: {response.status_code}")
            if response.status_code < 400:
                print(f"✅ {name} POST /sse handled successfully (Status: {response.status_code})")
            else:
                print(f"❌ {name} POST /sse failed (Status: {response.status_code})")
                print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ {name} Error: {e}")

async def main():
    await verify_post_sse(7015, "HeyGen")
    await verify_post_sse(8097, "YouTube")

if __name__ == "__main__":
    asyncio.run(main())
