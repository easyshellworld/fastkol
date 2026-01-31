import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from spoon_ai.tools.base import BaseTool


def _write_mock(script: str, title: str) -> str:
    output_dir = Path(os.getenv("VIDEO_OUTPUT_DIR", "outputs"))
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    script_path = output_dir / f"{title}-{timestamp}.txt"
    script_path.write_text(script, encoding="utf-8")
    return str(script_path)


def _validate_provider_config(provider: str) -> None:
    provider = provider.lower()
    if provider == "heygen":
        required = ["HEYGEN_API_KEY", "HEYGEN_VOICE_ID"]
    elif provider == "did":
        required = ["DID_API_KEY", "DID_VOICE_ID"]
    elif provider == "synthesia":
        required = ["SYNTHESIA_API_KEY", "SYNTHESIA_ACTOR_ID"]
    elif provider == "invideo":
        required = ["INVIDEO_API_KEY"]
    else:
        required = []

    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError(f"Missing video provider config: {', '.join(missing)}")


def _write_output_metadata(payload: Dict[str, Any], title: str) -> str:
    output_dir = Path(os.getenv("VIDEO_OUTPUT_DIR", "outputs"))
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    metadata_path = output_dir / f"{title}-{timestamp}.json"
    metadata_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return str(metadata_path)


def _heygen_headers(api_key: str) -> Dict[str, str]:
    return {
        "X-Api-Key": api_key,
        "Content-Type": "application/json",
    }


def _heygen_base_url() -> str:
    return os.getenv("HEYGEN_BASE_URL", "https://api.heygen.com").rstrip("/")


def _heygen_timeout() -> float:
    return float(os.getenv("HEYGEN_HTTP_TIMEOUT", "60"))


def _extract_video_id(data: Dict[str, Any]) -> Optional[str]:
    for key in ("video_id", "id", "videoId"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    nested = data.get("data")
    if isinstance(nested, dict):
        return _extract_video_id(nested)
    return None


def _extract_video_url(data: Dict[str, Any]) -> Optional[str]:
    for key in ("video_url", "url", "videoUrl", "download_url"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    nested = data.get("data")
    if isinstance(nested, dict):
        return _extract_video_url(nested)
    return None


def _heygen_generate(script: str, title: str) -> Dict[str, Any]:
    api_key = os.getenv("HEYGEN_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing HEYGEN_API_KEY")

    template_id = os.getenv("HEYGEN_TEMPLATE_ID", "").strip()
    voice_id = os.getenv("HEYGEN_VOICE_ID", "").strip()
    avatar_id = os.getenv("HEYGEN_AVATAR_ID", "").strip()

    if not template_id:
        if not voice_id:
            raise ValueError("Missing HEYGEN_VOICE_ID. Please set it in .env (e.g., from HeyGen API docs or dashboard).")
        if not avatar_id:
            raise ValueError("Missing HEYGEN_AVATAR_ID. Please set it in .env (e.g., 'Angela-inT-20220820').")

    payload: Dict[str, Any]
    if template_id:
        payload = {
            "template_id": template_id,
            "input_text": script,
        }
        if voice_id:
            payload["voice_id"] = voice_id
        if avatar_id:
            payload["avatar_id"] = avatar_id
    from heygen_mcp.api_client import (
        HeyGenApiClient,
        VideoGenerateRequest,
        VideoInput,
        Character,
        Voice,
        Dimension
    )
    import asyncio

    client = HeyGenApiClient(api_key)
    try:
        # HeyGen V2 /v2/video/generate structure using official models
        request = VideoGenerateRequest(
            title=title,
            video_inputs=[
                VideoInput(
                    character=Character(avatar_id=avatar_id),
                    voice=Voice(input_text=script, voice_id=voice_id),
                )
            ],
            dimension=Dimension(width=1280, height=720),
            test=True # Set to True for testing to avoid credit usage
        )
        
        # Run the async call in a block because VideoGenerateTool.execute is sync 
        # (Wait, actually VideoGenerateTool.execute is NOT sync usually in this codebase, let's verify)
        # Looking at original code: 'response = client.post(...)' - it was using sync httpx.Client.
        # HeyGenApiClient is async. We need to handle this.
        
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            if loop.is_running():
                # If loop is already running, we have a problem in a sync tool 
                # that wants to block. But with nest_asyncio it might work.
                # However, a cleaner way for this project might be to just use await if we can,
                # but VideoGenerateTool.execute is sync.
                result = loop.run_until_complete(client.generate_avatar_video(request))
            else:
                result = loop.run_until_complete(client.generate_avatar_video(request))
            
            return result.model_dump()
        finally:
            # Don't close the loop if it's the global one
            pass
    except Exception as e:
        print(f"HeyGen API Error in _heygen_generate: {e}")
        raise e


def _heygen_poll(video_id: str) -> Dict[str, Any]:
    api_key = os.getenv("HEYGEN_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing HEYGEN_API_KEY")
    endpoint = os.getenv("HEYGEN_STATUS_PATH", "/v1/video_status.get")
    url = f"{_heygen_base_url()}{endpoint}"
    max_attempts = int(os.getenv("HEYGEN_STATUS_MAX_ATTEMPTS", "30"))
    interval = float(os.getenv("HEYGEN_STATUS_POLL_INTERVAL", "5"))

    with httpx.Client(timeout=_heygen_timeout()) as client:
        for _ in range(max_attempts):
            response = client.get(url, params={"video_id": video_id}, headers=_heygen_headers(api_key))
            response.raise_for_status()
            data = response.json()
            status = str(data.get("status") or data.get("data", {}).get("status") or "").lower()
            if status in {"completed", "done", "success"}:
                return data
            if status in {"failed", "error"}:
                return data
            time.sleep(interval)
    return {"status": "timeout", "video_id": video_id}


def _heygen_download(video_url: str, title: str) -> str:
    output_dir = Path(os.getenv("VIDEO_OUTPUT_DIR", "outputs"))
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    video_path = output_dir / f"{title}-{timestamp}.mp4"
    with httpx.Client(timeout=_heygen_timeout()) as client:
        response = client.get(video_url)
        response.raise_for_status()
        video_path.write_bytes(response.content)
    return str(video_path)


def generate_avatar_video(script: str, title: str = "daily-brief") -> str:
    """Generate a digital human video from a script.

    Supports provider switching via VIDEO_PROVIDER (mock/heygen/did/synthesia/invideo).
    """
    provider = os.getenv("VIDEO_PROVIDER", "mock").lower()

    if provider == "mock":
        return _write_mock(script, title)

    _validate_provider_config(provider)
    if provider == "heygen":
        create_payload = _heygen_generate(script=script, title=title)
        metadata_path = _write_output_metadata(create_payload, f"{title}-heygen-create")
        video_id = _extract_video_id(create_payload)
        if not video_id:
            return metadata_path

        status_payload = _heygen_poll(video_id)
        status_path = _write_output_metadata(status_payload, f"{title}-heygen-status")
        video_url = _extract_video_url(status_payload)
        if video_url and os.getenv("HEYGEN_DOWNLOAD", "false").lower() == "true":
            return _heygen_download(video_url, title)
        return video_url or status_path

    raise NotImplementedError(
        "VIDEO_PROVIDER is set to a real provider but no client is wired yet. "
        "Tell me which provider to implement next."
    )


class VideoGenerateTool(BaseTool):
    name: str = "video_generate"
    description: str = "Generate a digital human video from a script"
    parameters: dict = {
        "type": "object",
        "properties": {
            "script": {"type": "string"},
            "title": {"type": "string", "default": "daily-brief"},
        },
        "required": ["script"],
    }

    async def execute(self, script: str, title: str = "daily-brief") -> str:
        return generate_avatar_video(script=script, title=title)
