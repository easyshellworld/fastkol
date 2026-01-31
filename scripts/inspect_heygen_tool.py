
import asyncio
from heygen_mcp.server import mcp
import json

async def inspect():
    print("Inspecting HeyGen MCP Tools...")
    tools = await mcp.list_tools()
    
    for tool in tools:
        if tool.name == "video_generate":
            print(f"\nTool: {tool.name}")
            print(f"Description: {tool.description}")
            print("Input Schema:")
            print(json.dumps(tool.inputSchema, indent=2))
            break
    else:
        print("Tool 'video_generate' not found.")

if __name__ == "__main__":
    asyncio.run(inspect())
