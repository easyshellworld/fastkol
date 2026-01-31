import os
import sys
from pathlib import Path
from typing import List

from spoon_ai.agents.spoon_react import SpoonReactAI
from spoon_ai.tools.mcp_tool import MCPTool
from spoon_ai.tools.tool_manager import ToolManager

from ..tools.polymarket import PolymarketEventsTool, PolymarketMarketsTool, PolymarketCompactTool
from ..tools.video import VideoGenerateTool
from ..tools.twitter import TwitterPostTool

from spoon_ai.schema import ToolChoice, AgentState
import asyncio
import logging
from termcolor import colored

# Setup logger
logger = logging.getLogger("spoon_ai")

class CustomSpoonReactAI(SpoonReactAI):
    def __init__(self, **kwargs):
        # Capture timeout before super() might ignore or reset it
        timeout_val = kwargs.get('timeout', 120.0)
        super().__init__(**kwargs)
        # Force set the default timeout to ensure it sticks
        self._default_timeout = float(timeout_val)
        
    async def think(self) -> bool:
        if self.next_step_prompt:
            await self.add_message("user", self.next_step_prompt)

        # Use cached MCP tools to avoid repeated server calls
        mcp_tools = await self._get_cached_mcp_tools()

        def convert_mcp_tool(tool) -> dict:
            params = getattr(tool, 'parameters', None) or getattr(tool, 'inputSchema', None) or {
                "type": "object",
                "properties": {},
                "required": []
            }
            return {
                "type": "function",
                "function": {
                    "name": getattr(tool, 'name', 'mcp_tool'),
                    "description": getattr(tool, 'description', 'MCP tool'),
                    "parameters": params
                }
            }

        all_tools = self.available_tools.to_params()
        mcp_tools_params = [convert_mcp_tool(tool) for tool in mcp_tools]
        unique_tools = {}
        for tool in all_tools + mcp_tools_params:
            tool_name = tool["function"]["name"]
            unique_tools[tool_name] = tool
        unique_tools_list = list(unique_tools.values())

        # FIX: Remove the hardcoded min(60.0) cap
        llm_timeout = getattr(self, '_default_timeout', 120.0)
        
        try:
            response = await asyncio.wait_for(
                self.llm.ask_tool(
                    messages=self.memory.messages,
                    system_msg=self.system_prompt,
                    tools=unique_tools_list,
                    tool_choice=self.tool_choices,
                    output_queue=self.output_queue,
                ),
                timeout=llm_timeout,
            )
        except asyncio.TimeoutError:
            logger.error(f"{self.name} LLM tool selection timed out after {llm_timeout}s")
            # Gracefully continue without tools
            await self.add_message("assistant", "Tool selection timed out.")
            self.tool_calls = []
            return False

        self.tool_calls = response.tool_calls

        if not self.tool_calls and self._should_terminate_on_finish_reason(response):
            logger.info(f"🏁 {self.name} terminating due to finish_reason signals (no tool calls)")
            self.state = AgentState.FINISHED
            await self.add_message("assistant", response.content or "Task completed")
            self._finish_reason_terminated = True
            self._final_response_content = response.content or "Task completed"
            return False

        # Reduce log verbosity
        logger.info(colored(f"🤔 {self.name}'s thoughts received (len={len(response.content) if response.content else 0})", "cyan"))
        tool_count = len(self.tool_calls) if self.tool_calls else 0
        if tool_count:
            logger.info(colored(f"🛠️ {self.name} selected {tool_count} tools", "green"))
        else:
            logger.info(colored(f"🛠️ {self.name} selected no tools", "yellow"))

        if self.output_queue:
            self.output_queue.put_nowait({"content": response.content})
            self.output_queue.put_nowait({"tool_calls": response.tool_calls})

        try:
            if self.tool_choices == ToolChoice.NONE:
                if response.tool_calls:
                    logger.warning(f"{self.name} selected {len(self.tool_calls)} tools, but tool_choice is NONE")
                    return False
                if response.content:
                    await self.add_message("assistant", response.content)
                    return True
                return False
            await self.add_message("assistant", response.content, tool_calls=self.tool_calls)
            if self.tool_choices == ToolChoice.REQUIRED and not self.tool_calls:
                return True
            if self.tool_choices == ToolChoice.AUTO and not self.tool_calls:
                return bool(response.content)
            return bool(self.tool_calls)
        except Exception as e:
            logger.error(f"{self.name} failed to think: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await self.add_message("assistant", f"Error encountered while thinking: {e}")
            return False

def create_react_agent() -> SpoonReactAI:
    tools: List[object] = [
        PolymarketEventsTool(),
        PolymarketMarketsTool(),
        PolymarketCompactTool(),
        VideoGenerateTool(),
        TwitterPostTool(),
    ]
    invideo_url = os.getenv("MCP_INVIDEO_URL")
    if invideo_url and invideo_url.strip().lower().startswith("http"):
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
    if heygen_url and heygen_url.strip().lower():
        # Use stdio for local HeyGen MCP
        script_path = str(Path("scripts/run_heygen_mcp.py").absolute())
        tools = [t for t in tools if not isinstance(t, VideoGenerateTool)]
        tools.append(
            MCPTool(
                name="heygen",
                description="HeyGen MCP tools",
                mcp_config={
                    "command": sys.executable,
                    "args": ["-u", script_path, "--stdio"],
                },
            )
        )
    
    youtube_url = os.getenv("MCP_YOUTUBE_URL")
    if youtube_url and youtube_url.strip().lower():
        # Use stdio for local YouTube MCP
        script_path = str(Path("src/mcp/youtube_server.py").absolute())
        tools.append(
            MCPTool(
                name="youtube",
                description="YouTube MCP tools",
                mcp_config={
                    "command": sys.executable,
                    "args": ["-u", script_path, "--stdio"],
                },
            )
        )

    return CustomSpoonReactAI(
        tools=ToolManager(tools),
        model="deepseek-chat",
        timeout=120
    )
