import httpx
import os
import asyncio
import sys

async def probe():
    url = "http://127.0.0.1:7013/sse"
    print(f"Probing {url}...")
    
    # Check for proxies
    print(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
    print(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
    print(f"NO_PROXY: {os.environ.get('NO_PROXY')}")
    
    try:
        async with httpx.AsyncClient(trust_env=False) as client:
            resp = await client.get(url, timeout=5.0)
            print(f"Response: {resp.status_code}")
            print(f"Headers: {resp.headers}")
    except httpx.ConnectError:
        print("Connection Refused! Is the server running on port 7013?")
    except Exception as e:
        import traceback
        print(f"Error Type: {type(e)}")
        print(f"Error Repr: {repr(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(probe())
