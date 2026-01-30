import os
from typing import Any, Dict, List, Optional
import json

import httpx

from spoon_ai.tools.base import BaseTool


GAMMA_BASE_URL = os.getenv("POLYMARKET_GAMMA_BASE_URL", "https://gamma-api.polymarket.com")


async def _get_json(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{GAMMA_BASE_URL}{path}"
    timeout = float(os.getenv("POLYMARKET_HTTP_TIMEOUT", "20"))
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_events(
    *,
    limit: int = 25,
    offset: int = 0,
    order: str = "id",
    ascending: bool = False,
    closed: Optional[bool] = False,
    tag_id: Optional[int] = None,
    related_tags: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "limit": limit,
        "offset": offset,
        "order": order,
        "ascending": ascending,
    }
    if closed is not None:
        params["closed"] = str(closed).lower()
    if tag_id is not None:
        params["tag_id"] = tag_id
    if related_tags is not None:
        params["related_tags"] = str(related_tags).lower()
    return await _get_json("/events", params=params)


async def fetch_markets(
    *,
    limit: int = 50,
    offset: int = 0,
    order: str = "volume",
    ascending: bool = False,
    active: Optional[bool] = True,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "limit": limit,
        "offset": offset,
        "order": order,
        "ascending": ascending,
    }
    if active is not None:
        params["active"] = str(active).lower()
    return await _get_json("/markets", params=params)


def _compact_str(value: Any, limit: int = 200) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _pick_keys(item: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    return {key: _compact_str(item.get(key)) for key in keys if key in item}


def _slim_event(event: Dict[str, Any]) -> Dict[str, Any]:
    keys = [
        "id",
        "title",
        "slug",
        "category",
        "volume",
        "volume24hr",
        "liquidity",
        "resolved",
        "closed",
        "start_time",
        "end_time",
    ]
    return _pick_keys(event, keys)


def _slim_market(market: Dict[str, Any]) -> Dict[str, Any]:
    keys = [
        "id",
        "question",
        "slug",
        "event_id",
        "active",
        "volume",
        "volume24hr",
        "liquidity",
        "outcomePrices",
        "outcomes",
    ]
    return _pick_keys(market, keys)


class PolymarketEventsTool(BaseTool):
    name: str = "polymarket_events"
    description: str = "Fetch Polymarket Gamma events for analysis"
    parameters: dict = {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "default": 25},
            "offset": {"type": "integer", "default": 0},
            "order": {"type": "string", "default": "id"},
            "ascending": {"type": "boolean", "default": False},
            "closed": {"type": "boolean", "default": False},
            "tag_id": {"type": "integer"},
            "related_tags": {"type": "boolean"},
        },
    }

    async def execute(
        self,
        limit: int = 25,
        offset: int = 0,
        order: str = "id",
        ascending: bool = False,
        closed: Optional[bool] = False,
        tag_id: Optional[int] = None,
        related_tags: Optional[bool] = None,
    ) -> str:
        events = await fetch_events(
            limit=limit,
            offset=offset,
            order=order,
            ascending=ascending,
            closed=closed,
            tag_id=tag_id,
            related_tags=related_tags,
        )
        return str(events)


class PolymarketMarketsTool(BaseTool):
    name: str = "polymarket_markets"
    description: str = "Fetch Polymarket Gamma markets for analysis"
    parameters: dict = {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "default": 50},
            "offset": {"type": "integer", "default": 0},
            "order": {"type": "string", "default": "volume"},
            "ascending": {"type": "boolean", "default": False},
            "active": {"type": "boolean", "default": True},
        },
    }

    async def execute(
        self,
        limit: int = 50,
        offset: int = 0,
        order: str = "volume",
        ascending: bool = False,
        active: Optional[bool] = True,
    ) -> str:
        markets = await fetch_markets(
            limit=limit,
            offset=offset,
            order=order,
            ascending=ascending,
            active=active,
        )
        return str(markets)


class PolymarketCompactTool(BaseTool):
    name: str = "polymarket_compact"
    description: str = "Fetch Polymarket events/markets and return a compact JSON payload"
    parameters: dict = {
        "type": "object",
        "properties": {
            "events_limit": {"type": "integer", "default": 6},
            "markets_limit": {"type": "integer", "default": 12},
        },
    }

    async def execute(self, events_limit: int = 6, markets_limit: int = 12) -> str:
        events = await fetch_events(limit=events_limit)
        markets = await fetch_markets(limit=markets_limit)
        payload = {
            "events": [_slim_event(event) for event in events],
            "markets": [_slim_market(market) for market in markets],
        }
        return json.dumps(payload, ensure_ascii=True)
