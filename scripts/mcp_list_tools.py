import asyncio
import json
import os
from mcp.client.session_group import ClientSessionGroup, StreamableHttpParameters


async def main() -> None:
    url = os.getenv("MCP_URL")
    if not url:
        raise SystemExit("MCP_URL is required")
    headers = None
    token = os.getenv("MCP_AUTH_TOKEN")
    if token:
        headers = {"Authorization": token}

    params = StreamableHttpParameters(url=url, headers=headers)
    async with ClientSessionGroup() as group:
        await group.connect_to_server(params)
        tools = group.tools
        payload = {}
        for name, tool in tools.items():
            payload[name] = {
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
