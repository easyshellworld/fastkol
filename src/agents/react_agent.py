import os
from typing import List

from spoon_ai.agents.spoon_react import SpoonReactAI
from spoon_ai.tools.mcp_tool import MCPTool
from spoon_ai.tools.tool_manager import ToolManager

from ..tools.polymarket import PolymarketEventsTool, PolymarketMarketsTool, PolymarketCompactTool
from ..tools.video import VideoGenerateTool
from ..tools.twitter import TwitterPostTool

def create_react_agent() -> SpoonReactAI:
    tools: List[object] = [
        PolymarketEventsTool(),
        PolymarketMarketsTool(),
        PolymarketCompactTool(),
        VideoGenerateTool(),
        TwitterPostTool(),
    ]
    invideo_url = os.getenv("MCP_INVIDEO_URL")
    if invideo_url:
        tools.append(
            MCPTool(
                name="invideo",
                description="InVideo MCP tools",
                mcp_config={
                    "url": invideo_url,
                    "transport": os.getenv("MCP_INVIDEO_TRANSPORT", "http"),
                },
            )
        )
    heygen_url = os.getenv("MCP_HEYGEN_URL")
    if heygen_url:
        tools.append(
            MCPTool(
                name="heygen",
                description="HeyGen MCP tools",
                mcp_config={
                    "url": heygen_url,
                    "transport": os.getenv("MCP_HEYGEN_TRANSPORT", "http"),
                },
            )
        )
    twitter_url = os.getenv("MCP_TWITTER_URL")
    if twitter_url:
        tools.append(
            MCPTool(
                name="twitter",
                description="Twitter/X MCP tools",
                mcp_config={
                    "url": twitter_url,
                    "transport": os.getenv("MCP_TWITTER_TRANSPORT", "http"),
                },
            )
        )
    youtube_url = os.getenv("MCP_YOUTUBE_URL")
    if youtube_url:
        tools.append(
            MCPTool(
                name="youtube",
                description="YouTube MCP tools",
                mcp_config={
                    "url": youtube_url,
                    "transport": os.getenv("MCP_YOUTUBE_TRANSPORT", "http"),
                },
            )
        )

    return SpoonReactAI(tools=ToolManager(tools))
