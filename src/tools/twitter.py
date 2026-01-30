import os
from typing import Optional

from spoon_ai.tools.base import BaseTool


def post_to_x(text: str, media_path: Optional[str] = None) -> str:
    """Stub for posting to X/Twitter.

    Replace this with a real API client once credentials are available.
    """
    enabled = os.getenv("ENABLE_TWITTER_POST", "false").lower() == "true"
    if not enabled:
        return "posting_skipped: ENABLE_TWITTER_POST=false"

    bearer = os.getenv("X_API_BEARER_TOKEN")
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_API_ACCESS_TOKEN")
    access_secret = os.getenv("X_API_ACCESS_SECRET")

    missing = [k for k, v in {
        "X_API_BEARER_TOKEN": bearer,
        "X_API_KEY": api_key,
        "X_API_SECRET": api_secret,
        "X_API_ACCESS_TOKEN": access_token,
        "X_API_ACCESS_SECRET": access_secret,
    }.items() if not v]

    if missing:
        return f"posting_failed: missing_credentials={','.join(missing)}"

    return "posting_stubbed: add X API integration"


class TwitterPostTool(BaseTool):
    name: str = "twitter_post"
    description: str = "Post a text update (and optional media) to X/Twitter"
    parameters: dict = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "media_path": {"type": "string"},
        },
        "required": ["text"],
    }

    async def execute(self, text: str, media_path: Optional[str] = None) -> str:
        return post_to_x(text, media_path=media_path)
