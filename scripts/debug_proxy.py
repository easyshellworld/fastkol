
import httpx
import asyncio
import os

async def test_proxy():
    url = "http://127.0.0.1:7013/sse"
    print(f"Testing connectivity to {url}")
    
    # Test 1: Default behavior (trust_env=True)
    print("\n--- Test 1: Default (trust_env=True) ---")
    try:
        async with httpx.AsyncClient(trust_env=True) as client:
            resp = await client.get(url, timeout=5)
            print(f"Status: {resp.status_code}")
            print("Success")
    except Exception as e:
        print(f"Failed: {e}")

    # Test 2: Ignore environment (trust_env=False)
    print("\n--- Test 2: Ignore Env (trust_env=False) ---")
    try:
        async with httpx.AsyncClient(trust_env=False) as client:
            resp = await client.get(url, timeout=5)
            print(f"Status: {resp.status_code}")
            print("Success")
    except Exception as e:
        print(f"Failed: {e}")
        
    # Check env vars
    print("\n--- Environment Variables ---")
    print(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
    print(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
    print(f"NO_PROXY: {os.environ.get('NO_PROXY')}")

if __name__ == "__main__":
    asyncio.run(test_proxy())
