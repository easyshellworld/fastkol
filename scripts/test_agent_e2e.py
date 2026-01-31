import os
import asyncio
from dotenv import load_dotenv
from src.agents.react_agent import create_react_agent

async def test_agent_e2e():
    load_dotenv()
    print("Initializing Agent with stdio-based MCP tools...")
    agent = create_react_agent()
    
    # We use a specific prompt to trigger heygen
    prompt = "Generate a 15s video about Spoon AI 'Hello World'. Use the heygen tool."
    print(f"Running prompt: {prompt}")
    
    try:
        # Based on src/main.py, the method is await agent.run(prompt)
        result = await agent.run(prompt)
        print("\n--- Agent Result ---")
        print(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Agent error: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_e2e())
