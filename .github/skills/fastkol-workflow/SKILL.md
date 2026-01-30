---
name: fastkol-workflow
summary: Generate Polymarket report, convert to narration script, and trigger video + Twitter publishing.
---

# fastKOL Backend Workflow Skill

Use this skill to execute the backend flow that matches fastkol_dev_docs.md.

## Steps
1) Fetch compact Polymarket data with `polymarket_compact`.
2) Produce a concise market report (markdown).
3) Convert the report into a short narration script (around 30s) for a digital human. The host should be female, female voice, and facing the camera.
4) Prefer InVideo MCP tools to generate a video from the narration script; if MCP tools are unavailable, call `video_generate`.
5) Prefer YouTube MCP tool `youtube_upload_video` for video publishing. If `YOUTUBE_THUMBNAIL_PATH` is set, call `youtube_set_thumbnail`. Then call `youtube_update_video_metadata` to finalize title/description/tags, and optionally `youtube_get_video_status` to confirm processing state. If YouTube MCP is unavailable, fall back to Twitter/X MCP `x_post_video` or skip.

## Inputs
- Optional: prompt or focus topic (default: Polymarket daily brief)

## Outputs
- report (markdown)
- narration script
- video result (URL/path)
- publish result (URL/status)
