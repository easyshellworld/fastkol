# Implementation Plan - Debug MCP Errors

We are facing two distinct issues:
1.  **502 Bad Gateway / Internal Server Error**: The MCP server is failing to handle requests properly, possibly due to the recently added middleware or environment issues.
2.  **400 Bad Request**: The HeyGen API is rejecting the video generation request, likely due to invalid parameters.

## User Review Required
> [!NOTE]
> We need to capture the server's internal error output effectively to diagnose the 502/500 issue.

## Proposed Changes

### 1. Diagnostic Tools
#### [NEW] [scripts/start_services_with_logs.py](file:///c:/Users/vip/fastkol/scripts/start_services_with_logs.py)
- A script to start MCP servers and redirect their `stdout` and `stderr` to log files (`server_heygen.log`, `server_youtube.log`).
- This will allow us to see the python traceback if the application is crashing.

### 2. Schema Inspection
#### [NEW] [scripts/inspect_heygen_tool.py](file:///c:/Users/vip/fastkol/scripts/inspect_heygen_tool.py)
- A script to print the input schema of `video_generate` tool to check for required fields.

## Verification Plan

### Automated Tests
1.  **Capture Logs**: Run `python scripts/start_services_with_logs.py`.
2.  **Trigger Error**: Run `python scripts/simulate_error.py`.
3.  **Analyze Logs**: Check `server_heygen.log` for tracebacks.
4.  **Inspect Schema**: Run `python scripts/inspect_heygen_tool.py`.

### Manual Fix
- Based on log findings, we will patch `run_heygen_mcp.py` (middleware) or `heygen_mcp` usage.
