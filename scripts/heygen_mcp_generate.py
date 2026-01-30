import asyncio
import json
import os
import sys
from typing import Any, Dict, Optional, Tuple

from mcp.client.session_group import ClientSessionGroup, StreamableHttpParameters, StdioServerParameters


def build_30s_script(text: str) -> str:
    return (
        "大家好，女主播正对镜头为你带来今天的 Polymarket 市场简报。"
        "加密市场流动性集中在比特币、以太坊、XRP 和 Solana，"
        "其中 1 月 31 日早 7 点美东的涨跌盘口流动性最高。"
        "15 分钟区间交易也更活跃，显示短线关注升温。"
        "体育方面，Valorant Game Changers EMEA 小组赛有中等流动性。"
        "以上信息仅供参考，不构成投资建议。"
    )


def _parse_content(result: Any) -> Any:
    if isinstance(result, dict):
        if "content" in result and isinstance(result["content"], list):
            items = result["content"]
            if items and isinstance(items[0], dict) and "text" in items[0]:
                text = items[0]["text"]
                try:
                    return json.loads(text)
                except Exception:
                    return text
        return result
    return result


def _pick_first_id(items: Any, key: str) -> Optional[str]:
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and item.get(key):
                return str(item[key])
    return None


def _find_voice_id(payload: Any) -> Optional[str]:
    voices = None
    if isinstance(payload, dict):
        voices = payload.get("voices") or payload.get("data") or payload.get("items")
    if not isinstance(voices, list):
        voices = payload if isinstance(payload, list) else []

    # Prefer female voices, prioritize Chinese/Mandarin when available.
    for lang_hint in ("Chinese", "Mandarin", "中文"):
        for voice in voices:
            if not isinstance(voice, dict):
                continue
            if str(voice.get("gender") or "").lower() != "female":
                continue
            if lang_hint.lower() in str(voice.get("language") or "").lower():
                vid = voice.get("voice_id") or voice.get("id")
                if vid:
                    return str(vid)

    for voice in voices:
        if not isinstance(voice, dict):
            continue
        if str(voice.get("gender") or "").lower() == "female":
            vid = voice.get("voice_id") or voice.get("id")
            if vid:
                return str(vid)

    return _pick_first_id(voices, "voice_id") or _pick_first_id(voices, "id")


def _pick_best_group(payload: Any) -> Tuple[Optional[str], Optional[str]]:
    groups = None
    if isinstance(payload, dict):
        groups = payload.get("avatar_groups") or payload.get("data") or payload.get("items")
    if not isinstance(groups, list):
        groups = payload if isinstance(payload, list) else []
    # Prefer non-PUBLIC_PHOTO groups (likely usable for video) and ones with default_voice_id.
    for g in groups:
        if not isinstance(g, dict):
            continue
        if g.get("group_type") and g.get("group_type") != "PUBLIC_PHOTO":
            gid = g.get("group_id") or g.get("id")
            if gid:
                return str(gid), g.get("default_voice_id")
    for g in groups:
        if not isinstance(g, dict):
            continue
        gid = g.get("group_id") or g.get("id")
        if gid:
            return str(gid), g.get("default_voice_id")
    return None, None


def _find_avatar_and_default_voice(payload: Any) -> Tuple[Optional[str], Optional[str]]:
    avatars = None
    if isinstance(payload, dict):
        avatars = payload.get("avatars") or payload.get("data") or payload.get("items")
    if isinstance(avatars, list):
        preferred_names = {"maria", "annie", "sophia", "emily", "grace", "ava", "olivia", "lily", "emma"}
        for avatar in avatars:
            if not isinstance(avatar, dict):
                continue
            name = str(avatar.get("name") or avatar.get("avatar_name") or "").strip().lower()
            if name and name in preferred_names:
                avatar_id = avatar.get("avatar_id") or avatar.get("id")
                default_voice = avatar.get("default_voice_id")
                if avatar_id:
                    return str(avatar_id), str(default_voice) if default_voice else None
        for avatar in avatars:
            if not isinstance(avatar, dict):
                continue
            avatar_id = avatar.get("avatar_id") or avatar.get("id")
            default_voice = avatar.get("default_voice_id")
            if avatar_id:
                return str(avatar_id), str(default_voice) if default_voice else None
        if avatars and isinstance(avatars[0], dict):
            avatar = avatars[0]
            return str(avatar.get("avatar_id") or avatar.get("id")), avatar.get("default_voice_id")
    return None, None


def _extract_video_id(payload: Any) -> Optional[str]:
    if isinstance(payload, dict):
        for key in ("video_id", "id", "videoId"):
            if payload.get(key):
                return str(payload[key])
        if isinstance(payload.get("data"), dict):
            return _extract_video_id(payload["data"])
    return None


def _extract_video_url(payload: Any) -> Optional[str]:
    if isinstance(payload, dict):
        for key in ("video_url", "url", "videoUrl", "download_url"):
            if payload.get(key):
                return str(payload[key])
        if isinstance(payload.get("data"), dict):
            return _extract_video_url(payload["data"])
    return None


def _tool_schema(tool: Any) -> Dict[str, Any]:
    if hasattr(tool, "inputSchema"):
        return tool.inputSchema or {}
    if isinstance(tool, dict):
        return tool.get("inputSchema", {})
    return {}


async def _connect(group: ClientSessionGroup):
    use_stdio = os.getenv("MCP_HEYGEN_STDIO", "1") == "1"
    if use_stdio:
        cmd = os.getenv("HEYGEN_MCP_CMD", "/home/userkevin/lx_dao/hackason_spark_ai/venv/bin/python")
        args = ["-m", "heygen_mcp.server"]
        env = os.environ.copy()
        params = StdioServerParameters(command=cmd, args=args, env=env)
    else:
        url = os.getenv("MCP_HEYGEN_URL") or os.getenv("MCP_URL")
        if not url:
            raise SystemExit("MCP_HEYGEN_URL or MCP_URL is required")
        headers = None
        token = os.getenv("MCP_AUTH_TOKEN")
        if token:
            headers = {"Authorization": token}
        params = StreamableHttpParameters(url=url, headers=headers)
    await group.connect_to_server(params)


async def main() -> None:
    script_input = sys.stdin.read().strip()
    if not script_input:
        raise SystemExit("Input text is required via stdin")
    narration = build_30s_script(script_input)

    async with ClientSessionGroup() as group:
        await _connect(group)
        tools = group.tools

        if "generate_avatar_video" not in tools:
            print("HeyGen MCP tools not found or not loaded.")
            print("Available tools:", list(tools.keys()))
            return

        voice_id = None
        if "get_voices" in tools:
            voices = await group.call_tool("get_voices", {})
            voice_payload = _parse_content(voices.model_dump())
            voice_id = _find_voice_id(voice_payload)

        avatar_id = None
        if "get_avatar_groups" in tools:
            groups = await group.call_tool("get_avatar_groups", {"include_public": True})
            group_payload = _parse_content(groups.model_dump())
            group_id, group_default_voice = _pick_best_group(group_payload)
            if group_id and "get_avatars_in_avatar_group" in tools:
                avatars = await group.call_tool("get_avatars_in_avatar_group", {"group_id": group_id})
                avatar_payload = _parse_content(avatars.model_dump())
                avatar_id, default_voice = _find_avatar_and_default_voice(avatar_payload)
                if not voice_id and default_voice:
                    voice_id = default_voice
            if not voice_id and group_default_voice:
                voice_id = group_default_voice

        if not avatar_id:
            avatar_id = os.getenv("HEYGEN_AVATAR_ID") or None
        if not voice_id:
            voice_id = os.getenv("HEYGEN_VOICE_ID") or None

        if not avatar_id or not voice_id:
            print(json.dumps({
                "error": "Missing avatar_id or voice_id. Provide HEYGEN_AVATAR_ID/HEYGEN_VOICE_ID or ensure MCP returns defaults.",
                "avatar_id": avatar_id,
                "voice_id": voice_id,
            }, ensure_ascii=False, indent=2))
            return

        schema = _tool_schema(tools["generate_avatar_video"])
        args: Dict[str, Any] = {}
        for key in ("input_text", "text", "script"):
            if key in schema.get("properties", {}):
                args[key] = narration
                break
        if "voice_id" in schema.get("properties", {}):
            args["voice_id"] = voice_id
        if "avatar_id" in schema.get("properties", {}):
            args["avatar_id"] = avatar_id
        if "title" in schema.get("properties", {}):
            args["title"] = "polymarket-daily"

        result = await group.call_tool("generate_avatar_video", args)
        payload = _parse_content(result.model_dump())
        video_id = _extract_video_id(payload)
        video_url = _extract_video_url(payload)

        if not video_url and video_id and "get_avatar_video_status" in tools:
            status = await group.call_tool("get_avatar_video_status", {"video_id": video_id})
            status_payload = _parse_content(status.model_dump())
            video_url = _extract_video_url(status_payload)

        print(json.dumps({
            "voice_id": voice_id,
            "avatar_id": avatar_id,
            "video_id": video_id,
            "video_url": video_url,
            "raw": payload,
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
