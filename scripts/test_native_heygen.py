import os
import asyncio
import httpx
from dotenv import load_dotenv
from src.tools.video import VideoGenerateTool

async def test_native():
    load_dotenv()
    tool = VideoGenerateTool()
    print("Testing native VideoGenerateTool...")
    try:
        # We use a very short script to save credits and time
        result = await tool.execute(script="Hello, this is a test.", title="test-native-fix")
        print(f"Result: {result}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error {e.response.status_code}: {e.response.text}")
    except Exception:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_native())
