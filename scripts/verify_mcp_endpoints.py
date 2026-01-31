import httpx
import asyncio

async def check(url):
    print(f"Checking {url}...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)  # GET for SSE endpoint usually connects
            print(f"Status: {resp.status_code}")
            print(f"Headers: {resp.headers}")
            print(f"Content: {resp.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    await check("http://127.0.0.1:7013/sse")
    await check("http://127.0.0.1:8095/sse")

if __name__ == "__main__":
    asyncio.run(main())
