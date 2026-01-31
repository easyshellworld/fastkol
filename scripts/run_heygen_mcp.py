import os
import uvicorn
from dotenv import load_dotenv
from heygen_mcp.server import mcp

load_dotenv()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdio", action="store_true")
    args = parser.parse_args()

    if args.stdio:
        mcp.run()
        return

    host = os.getenv("HEYGEN_MCP_HOST", "127.0.0.1")
    port = int(os.getenv("HEYGEN_MCP_PORT", "7013"))
    
    print(f"Starting HeyGen MCP Server explicitly on http://{host}:{port}")

    # Alias video_generate to generate_avatar_video for Spoon AI compatibility
    try:
        from heygen_mcp.server import generate_avatar_video
        
        # We need to manually register it because decorators run at module level
        # and mcp object is already imported. 
        # But FastMCP allows late registration.
        @mcp.tool(name="video_generate")
        async def video_generate(avatar_id: str, input_text: str, voice_id: str, title: str = ""):
            """Alias for generate_avatar_video to support Spoon AI."""
            print(f"DEBUG: video_generate alias called with {avatar_id}, {len(input_text)} chars")
            return await generate_avatar_video(avatar_id=avatar_id, input_text=input_text, voice_id=voice_id, title=title)
        
        print("DEBUG: Registered video_generate alias")
    except ImportError:
        print("WARNING: Could not import generate_avatar_video to create alias")
    except Exception as e:
        print(f"WARNING: Failed to register alias: {e}")
    
    # FastMCP exposes the underlying Starlette/FastAPI app as `sse_app`
    # We run this directly with uvicorn to have full control over host/port
    if hasattr(mcp, 'sse_app'):
        app = mcp.sse_app()
    elif hasattr(mcp, '_sse_app'):
        app = mcp._sse_app
    else:
        # Fallback if sse_app is not available
        print("Error: mcp object does not have sse_app. Cannot bind port reliably.")
        return

    # Spoon AI Workaround: Redirect POST /sse to /messages
    async def middleware_app(scope, receive, send):
        if scope["type"] == "http":
            method = scope.get("method", "")
            path = scope.get("path", "")
            print(f"DEBUG [HeyGen]: {method} {path}")
            if method == "POST" and path == "/sse":
                print(f"DEBUG [HeyGen]: Redirecting to /messages/ for Spoon AI compatibility")
                scope["path"] = "/messages/"
                scope["raw_path"] = b"/messages/"
        try:
            await app(scope, receive, send)
        except Exception as e:
            print(f"ERROR [HeyGen]: {e}")
            raise e

    uvicorn.run(middleware_app, host=host, port=port)

if __name__ == "__main__":
    main()
