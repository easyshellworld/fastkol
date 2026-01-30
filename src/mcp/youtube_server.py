import os
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP


def _env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def _token_endpoint() -> str:
    return os.getenv("YOUTUBE_TOKEN_URL", "https://oauth2.googleapis.com/token")


def _api_base() -> str:
    return os.getenv("YOUTUBE_API_BASE_URL", "https://www.googleapis.com").rstrip("/")


def _upload_base() -> str:
    return os.getenv("YOUTUBE_UPLOAD_BASE_URL", "https://www.googleapis.com/upload").rstrip("/")


def _get_access_token() -> str:
    client_id = _env_required("YOUTUBE_CLIENT_ID")
    client_secret = _env_required("YOUTUBE_CLIENT_SECRET")
    refresh_token = _env_required("YOUTUBE_REFRESH_TOKEN")
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    with httpx.Client(timeout=30) as client:
        response = client.post(_token_endpoint(), data=data)
        response.raise_for_status()
        payload = response.json()
    access_token = payload.get("access_token")
    if not access_token:
        raise ValueError(f"Missing access_token in response: {payload}")
    return str(access_token)


def _initiate_resumable_upload(
    access_token: str,
    title: str,
    description: str,
    tags: Optional[List[str]],
    category_id: Optional[str],
    privacy_status: str,
    made_for_kids: bool,
) -> str:
    url = f"{_upload_base()}/youtube/v3/videos"
    params = {"uploadType": "resumable", "part": "snippet,status"}
    snippet: Dict[str, object] = {"title": title, "description": description}
    if tags:
        snippet["tags"] = tags
    if category_id:
        snippet["categoryId"] = category_id
    status = {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": made_for_kids}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
    }
    body = {"snippet": snippet, "status": status}
    with httpx.Client(timeout=60) as client:
        response = client.post(url, params=params, json=body, headers=headers)
        response.raise_for_status()
        upload_url = response.headers.get("Location")
    if not upload_url:
        raise ValueError("Missing resumable upload URL (Location header).")
    return upload_url


def _upload_video_file(upload_url: str, file_path: str, content_type: str) -> Dict[str, object]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    size = path.stat().st_size
    headers = {
        "Content-Type": content_type,
        "Content-Length": str(size),
    }
    with path.open("rb") as handle:
        with httpx.Client(timeout=300) as client:
            response = client.put(upload_url, content=handle, headers=headers)
            response.raise_for_status()
            return response.json()


def _videos_update(
    access_token: str,
    video_id: str,
    title: Optional[str],
    description: Optional[str],
    tags: Optional[List[str]],
    category_id: Optional[str],
    privacy_status: Optional[str],
    made_for_kids: Optional[bool],
    contains_synthetic_media: Optional[bool],
) -> Dict[str, object]:
    url = f"{_api_base()}/youtube/v3/videos"
    snippet: Dict[str, object] = {}
    status: Dict[str, object] = {}
    if title is not None:
        snippet["title"] = title
    if description is not None:
        snippet["description"] = description
    if tags is not None:
        snippet["tags"] = tags
    if category_id is not None:
        snippet["categoryId"] = category_id
    if privacy_status is not None:
        status["privacyStatus"] = privacy_status
    if made_for_kids is not None:
        status["selfDeclaredMadeForKids"] = made_for_kids
    if contains_synthetic_media is not None:
        status["containsSyntheticMedia"] = contains_synthetic_media

    parts = []
    body: Dict[str, object] = {"id": video_id}
    if snippet:
        body["snippet"] = snippet
        parts.append("snippet")
    if status:
        body["status"] = status
        parts.append("status")
    if not parts:
        raise ValueError("No fields provided to update.")

    params = {"part": ",".join(parts)}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=60) as client:
        response = client.put(url, params=params, json=body, headers=headers)
        response.raise_for_status()
        return response.json()


def _videos_list(access_token: str, video_id: str, parts: str) -> Dict[str, object]:
    url = f"{_api_base()}/youtube/v3/videos"
    params = {"part": parts, "id": video_id}
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    with httpx.Client(timeout=30) as client:
        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


def _thumbnails_set(access_token: str, video_id: str, image_path: str, content_type: str) -> Dict[str, object]:
    url = f"{_upload_base()}/youtube/v3/thumbnails/set"
    params = {"videoId": video_id}
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": content_type}
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Thumbnail not found: {image_path}")
    with path.open("rb") as handle:
        with httpx.Client(timeout=60) as client:
            response = client.post(url, params=params, content=handle, headers=headers)
            response.raise_for_status()
            return response.json()


server = FastMCP("fastkol-youtube-mcp")


@server.tool()
def youtube_upload_video(
    file_path: str,
    title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    category_id: Optional[str] = None,
    privacy_status: str = "unlisted",
    made_for_kids: bool = False,
    content_type: str = "video/mp4",
) -> Dict[str, object]:
    """Upload a video to YouTube using a resumable upload session."""
    access_token = _get_access_token()
    upload_url = _initiate_resumable_upload(
        access_token=access_token,
        title=title,
        description=description,
        tags=tags,
        category_id=category_id,
        privacy_status=privacy_status,
        made_for_kids=made_for_kids,
    )
    payload = _upload_video_file(upload_url, file_path, content_type)
    video_id = payload.get("id")
    return {
        "video_id": video_id,
        "video_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else None,
        "raw": payload,
    }


@server.tool()
def youtube_update_video_metadata(
    video_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    category_id: Optional[str] = None,
    privacy_status: Optional[str] = None,
    made_for_kids: Optional[bool] = None,
    contains_synthetic_media: Optional[bool] = None,
) -> Dict[str, object]:
    """Update YouTube video metadata (snippet/status)."""
    access_token = _get_access_token()
    payload = _videos_update(
        access_token=access_token,
        video_id=video_id,
        title=title,
        description=description,
        tags=tags,
        category_id=category_id,
        privacy_status=privacy_status,
        made_for_kids=made_for_kids,
        contains_synthetic_media=contains_synthetic_media,
    )
    return {"video_id": video_id, "raw": payload}


@server.tool()
def youtube_get_video_status(video_id: str, parts: str = "status,processingDetails") -> Dict[str, object]:
    """Fetch video status/processing details."""
    access_token = _get_access_token()
    payload = _videos_list(access_token=access_token, video_id=video_id, parts=parts)
    return {"video_id": video_id, "raw": payload}


@server.tool()
def youtube_set_thumbnail(
    video_id: str,
    image_path: str,
    content_type: str = "image/jpeg",
) -> Dict[str, object]:
    """Upload and set a custom thumbnail for a video."""
    access_token = _get_access_token()
    payload = _thumbnails_set(
        access_token=access_token,
        video_id=video_id,
        image_path=image_path,
        content_type=content_type,
    )
    return {"video_id": video_id, "raw": payload}


if __name__ == "__main__":
    os.environ.setdefault("FASTMCP_HOST", os.getenv("YOUTUBE_MCP_HOST", "127.0.0.1"))
    os.environ.setdefault("FASTMCP_PORT", os.getenv("YOUTUBE_MCP_PORT", "7020"))
    server.run(transport="streamable-http")
