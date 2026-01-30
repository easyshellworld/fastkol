import argparse
import asyncio

from dotenv import load_dotenv

from src.agents.react_agent import create_react_agent
from src.agents.polymarket_graph import build_daily_graph


async def run_react(prompt: str) -> None:
    agent = create_react_agent()
    result = await agent.run(prompt)
    print(result)


async def run_graph() -> None:
    agent = build_daily_graph()
    result = await agent.run("polymarket daily brief")
    print(result)


def _default_react_prompt() -> str:
    return (
        "fastKOL backend mode.\n"
        "1) Use polymarket_compact.\n"
        "2) Write a concise Polymarket report (markdown).\n"
        "3) If video generation is enabled, generate a 30s narration script (female host, facing camera).\n"
        "4) Prefer YouTube MCP: upload video, set thumbnail if available, update metadata, check status.\n"
        "Return report + narration + any publish result."
    )


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["react", "graph"], default="react")
    parser.add_argument("--prompt", default=_default_react_prompt())
    args = parser.parse_args()

    if args.mode == "react":
        asyncio.run(run_react(args.prompt))
    else:
        asyncio.run(run_graph())


if __name__ == "__main__":
    main()
