
import httpx
import asyncio

async def test_endpoint(url, method="POST"):
    print(f"Testing {method} {url}...")
    try:
        async with httpx.AsyncClient(trust_env=False) as client:
            if method == "POST":
                # Send valid JSON-RPC to avoid 500 Internal Server Error due to empty body
                payload = {
                    "jsonrpc": "2.0",
                    "method": "listTools",
                    "id": 1,
                    "params": {}
                }
                response = await client.post(url, json=payload)
            else:
                response = await client.get(url, timeout=5.0)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Content: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    await test_endpoint("http://127.0.0.1:7013/sse", "POST")
    await test_endpoint("http://127.0.0.1:8095/sse", "POST")
    # Also test GET to confirm they are alive
    await test_endpoint("http://127.0.0.1:7013/sse", "GET")
    await test_endpoint("http://127.0.0.1:8095/sse", "GET")

if __name__ == "__main__":
    asyncio.run(main())
