import httpx
import asyncio
import os

async def probe_sse():
    url = "http://127.0.0.1:7013/sse"
    print(f"Connecting to {url} (Streaming)...")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            async with client.stream("GET", url) as response:
                print(f"Status Code: {response.status_code}")
                print(f"Headers: {response.headers}")
                
                if response.status_code == 200:
                    print("✅ Connection Successful!")
                    if "text/event-stream" in response.headers.get("content-type", ""):
                         print("✅ Correct Content-Type: text/event-stream")
                    else:
                         print("⚠️ User Warning: Content-Type is not text/event-stream")
                else:
                    print(f"❌ Server returned status {response.status_code}")
                    
    except httpx.ConnectError:
        print("❌ Connection Refused! Is the server running?")
    except httpx.ReadTimeout:
        print("⚠️ Read Timeout (Initial Handshake). Server accepted connection but sent no data.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe_sse())
