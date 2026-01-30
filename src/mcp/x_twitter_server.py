import base64
import hashlib
import hmac
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from urllib.parse import quote, urlencode, urlsplit, urlunsplit

import httpx
from mcp.server.fastmcp import FastMCP


def _percent_encode(value: str) -> str:
    return quote(value, safe="~")


def _normalized_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _collect_params(params: Dict[str, str]) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    for key, value in params.items():
        if value is None:
            continue
        items.append((str(key), str(value)))
    items.sort(key=lambda kv: (kv[0], kv[1]))
    return items


def _oauth1_header(
    method: str,
    url: str,
    params: Dict[str, str],
    consumer_key: str,
    consumer_secret: str,
    token: str,
    token_secret: str,
) -> str:
    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": token,
        "oauth_version": "1.0",
    }

    signature_params = dict(params)
    signature_params.update(oauth_params)
    normalized = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}"
        for k, v in _collect_params(signature_params)
    )
    base_elems = [
        method.upper(),
        _percent_encode(_normalized_url(url)),
        _percent_encode(normalized),
    ]
    base_string = "&".join(base_elems)
    signing_key = f"{_percent_encode(consumer_secret)}&{_percent_encode(token_secret)}"
    digest = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    oauth_params["oauth_signature"] = base64.b64encode(digest).decode()

    header = ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )
    return f"OAuth {header}"


def _env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def _x_api_base() -> str:
    return os.getenv("X_API_BASE_URL", "https://api.x.com").rstrip("/")


def _x_upload_base() -> str:
    return os.getenv("X_UPLOAD_BASE_URL", "https://upload.twitter.com").rstrip("/")


def _chunk_size() -> int:
    return int(os.getenv("X_MEDIA_CHUNK_SIZE", "1048576"))


def _processing_poll_interval() -> float:
    return float(os.getenv("X_MEDIA_STATUS_INTERVAL", "5"))


def _processing_max_attempts() -> int:
    return int(os.getenv("X_MEDIA_STATUS_MAX_ATTEMPTS", "30"))


def _auth_header(method: str, url: str, params: Dict[str, str]) -> str:
    consumer_key = _env_required("X_API_KEY")
    consumer_secret = _env_required("X_API_SECRET")
    token = _env_required("X_API_ACCESS_TOKEN")
    token_secret = _env_required("X_API_ACCESS_SECRET")
    return _oauth1_header(
        method=method,
        url=url,
        params=params,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        token=token,
        token_secret=token_secret,
    )


def _upload_init(file_path: str, media_type: str, media_category: str) -> str:
    url = f"{_x_upload_base()}/1.1/media/upload.json"
    total_bytes = str(Path(file_path).stat().st_size)
    params = {
        "command": "INIT",
        "media_type": media_type,
        "total_bytes": total_bytes,
        "media_category": media_category,
    }
    headers = {"Authorization": _auth_header("POST", url, params)}
    with httpx.Client(timeout=60) as client:
        response = client.post(url, data=params, headers=headers)
        response.raise_for_status()
        payload = response.json()
        return str(payload.get("media_id_string") or payload.get("media_id"))


def _upload_append(file_path: str, media_id: str) -> None:
    url = f"{_x_upload_base()}/1.1/media/upload.json"
    size = _chunk_size()
    segment_index = 0
    with open(file_path, "rb") as handle:
        while True:
            chunk = handle.read(size)
            if not chunk:
                break
            params = {
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": str(segment_index),
            }
            headers = {"Authorization": _auth_header("POST", url, params)}
            files = {"media": chunk}
            with httpx.Client(timeout=60) as client:
                response = client.post(url, data=params, files=files, headers=headers)
                response.raise_for_status()
            segment_index += 1


def _upload_finalize(media_id: str) -> Dict[str, object]:
    url = f"{_x_upload_base()}/1.1/media/upload.json"
    params = {"command": "FINALIZE", "media_id": media_id}
    headers = {"Authorization": _auth_header("POST", url, params)}
    with httpx.Client(timeout=60) as client:
        response = client.post(url, data=params, headers=headers)
        response.raise_for_status()
        return response.json()


def _upload_status(media_id: str) -> Dict[str, object]:
    url = f"{_x_upload_base()}/1.1/media/upload.json"
    params = {"command": "STATUS", "media_id": media_id}
    headers = {"Authorization": _auth_header("GET", url, params)}
    with httpx.Client(timeout=60) as client:
        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


def _wait_for_processing(media_id: str) -> Dict[str, object]:
    for _ in range(_processing_max_attempts()):
        payload = _upload_status(media_id)
        processing = payload.get("processing_info") or {}
        state = str(processing.get("state") or "").lower()
        if state in {"succeeded", "failed"}:
            return payload
        time.sleep(_processing_poll_interval())
    return {"media_id": media_id, "processing_info": {"state": "timeout"}}


def _post_tweet(text: str, media_id: str | None = None) -> Dict[str, object]:
    url = f"{_x_api_base()}/2/tweets"
    params: Dict[str, str] = {}
    headers = {"Authorization": _auth_header("POST", url, params), "Content-Type": "application/json"}
    body: Dict[str, object] = {"text": text}
    if media_id:
        body["media"] = {"media_ids": [media_id]}
    with httpx.Client(timeout=60) as client:
        response = client.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()


server = FastMCP("fastkol-x-mcp")


@server.tool()
def x_upload_video(
    file_path: str,
    media_type: str = "video/mp4",
    media_category: str = "tweet_video",
) -> Dict[str, object]:
    """Upload a video to X and return media_id and status."""
    media_id = _upload_init(file_path, media_type, media_category)
    _upload_append(file_path, media_id)
    finalize_payload = _upload_finalize(media_id)
    if finalize_payload.get("processing_info"):
        status_payload = _wait_for_processing(media_id)
        return {"media_id": media_id, "finalize": finalize_payload, "status": status_payload}
    return {"media_id": media_id, "finalize": finalize_payload}


@server.tool()
def x_post_tweet(text: str, media_id: str | None = None) -> Dict[str, object]:
    """Create a tweet with optional media_id."""
    return _post_tweet(text=text, media_id=media_id)


@server.tool()
def x_post_video(text: str, file_path: str) -> Dict[str, object]:
    """Upload a video and create a tweet in one call."""
    upload_result = x_upload_video(file_path=file_path)
    media_id = upload_result.get("media_id")
    tweet_result = _post_tweet(text=text, media_id=media_id)
    return {"upload": upload_result, "tweet": tweet_result}


if __name__ == "__main__":
    os.environ.setdefault("FASTMCP_HOST", os.getenv("X_MCP_HOST", "127.0.0.1"))
    os.environ.setdefault("FASTMCP_PORT", os.getenv("X_MCP_PORT", "7010"))
    server.run(transport="streamable-http")
