import json
import os
import time
import logging
import asyncio
import httpx
from dotenv import load_dotenv

# --- Monkeypatch httpx for Gemini Rate Limiting ---
# Gemini Free Tier is limited to 15 RPM (1 req / 4s) or 2 RPM (1 req / 30s) depending on model.
# We enforce a global 4s delay between calls to 'generativelanguage' to be safe.

original_post = httpx.AsyncClient.post
GEMINI_LOCK = asyncio.Lock()
NEXT_ALLOWED_TIME = 0
GEMINI_DELAY = 4.0

async def rate_limited_post(self, url, *args, **kwargs):
    global NEXT_ALLOWED_TIME
    url_str = str(url)
    if not "generativelanguage.googleapis.com" in url_str:
        return await original_post(self, url, *args, **kwargs)

    retries = 5
    for attempt in range(retries):
        # 1. Wait for our local rate limiter slot
        async with GEMINI_LOCK:
            now = time.time()
            wait_start = max(now, NEXT_ALLOWED_TIME)
            NEXT_ALLOWED_TIME = wait_start + GEMINI_DELAY
            sleep_duration = wait_start - now
        
        if sleep_duration > 0:
            print(f"[{attempt+1}/{retries}] Rate limiting {url_str} | Queueing for: {sleep_duration:.2f}s")
            await asyncio.sleep(sleep_duration)

        # 2. Make the actual request
        response = await original_post(self, url, *args, **kwargs)

        # 3. Handle 429 Response from Google
        if response.status_code == 429:
            print(f"[{attempt+1}/{retries}] Hit 429 from Gemini! Backing off...")
            # If we hit a real 429, our local timer was too aggressive or state was stale.
            # Force a longer delay for the next attempt.
            async with GEMINI_LOCK:
                NEXT_ALLOWED_TIME = time.time() + (10.0 * (attempt + 1))
            continue
            
        return response
    
    # If all retries failed, return the last response (likely 429)
    return response

httpx.AsyncClient.post = rate_limited_post
# --------------------------------------------------

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.agents.react_agent import create_react_agent

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
class WebSocketHandler(logging.Handler):
    def __init__(self, websocket: WebSocket):
        super().__init__()
        self.websocket = websocket

    def emit(self, record):
        try:
            msg = self.format(record)
            # Create a simple JSON structure for the frontend to parse
            data = {
                "type": "log",
                "message": msg,
                "level": record.levelname
            }
            # We need to schedule the send_text coroutine
            asyncio.create_task(self.websocket.send_text(json.dumps(data)))
        except Exception:
            self.handleError(record)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Setup custom logger handler for this connection
    handler = WebSocketHandler(websocket)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Attach to root logger
    root_logger = logging.getLogger()
    
    # Ensure logs also go to console (stdout)
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "start":
                await websocket.send_text(json.dumps({"type": "status", "stage": "start", "message": "Workflow started"}))
                
                try:
                    # Run the agent
                    # We define the specific prompt for the workflow
                    prompt = (
                        "fastKOL backend mode.\n"
                        "1) Use polymarket_compact to find top crypto markets. "
                        "2) Write a concise Polymarket report (markdown). "
                        "3) Generate a 15s narration script (female host, facing camera, approx 30 words). "
                        "4) THEN, use the 'heygen' MCP tool (generate_avatar_video) to create a video from the script. "
                        "   (Do NOT use the legacy VideoGenerateTool/video_generate). "
                        "5) Finally, use YouTube MCP tool to upload the video (set privacy=unlisted). "
                        "Return the report + video URL."
                    )
                    
                    agent = create_react_agent()
                    # Run agent in executor to avoid blocking the event loop if it's synchronous
                    # If agent.run is async, await it directly. src/main.py suggests it IS async.
                    result = await agent.run(prompt)
                    
                    await websocket.send_text(json.dumps({
                        "type": "result", 
                        "data": str(result),
                        "message": "Workflow completed"
                    }))
                    
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error", 
                        "message": str(e)
                    }))
                    root_logger.error(f"Agent execution failed: {e}")

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        root_logger.removeHandler(handler)
