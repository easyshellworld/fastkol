import subprocess
import sys
import time
import os
from pathlib import Path

def start_services():
    base_dir = Path(__file__).parent.parent
    
    # 1. Start HeyGen MCP
    heygen_script = base_dir / "scripts" / "run_heygen_mcp.py"
    print(f"Starting HeyGen MCP from {heygen_script}...")
    heygen_process = subprocess.Popen(
        [sys.executable, str(heygen_script)],
        cwd=str(base_dir)
    )
    
    # 2. Start YouTube MCP
    youtube_script = base_dir / "src" / "mcp" / "youtube_server.py"
    print(f"Starting YouTube MCP from {youtube_script}...")
    youtube_process = subprocess.Popen(
        [sys.executable, str(youtube_script)],
        cwd=str(base_dir)
    )
    
    print("Services started. Waiting for initialization...")
    time.sleep(5)
    
    print(f"HeyGen PID: {heygen_process.pid}")
    print(f"YouTube PID: {youtube_process.pid}")
    
    try:
        while True:
            time.sleep(1)
            if heygen_process.poll() is not None:
                print(f"HeyGen MCP exited with code {heygen_process.returncode}")
                break
            if youtube_process.poll() is not None:
                print(f"YouTube MCP exited with code {youtube_process.returncode}")
                break
    except KeyboardInterrupt:
        print("Stopping services...")
        heygen_process.terminate()
        youtube_process.terminate()
        print("Services stopped.")

if __name__ == "__main__":
    start_services()
