import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict

from spoon_ai.chat import ChatBot
from spoon_ai.graph import StateGraph, START, END, GraphAgent

from ..tools.polymarket import fetch_events, fetch_markets
from ..tools.video import generate_avatar_video
from ..tools.twitter import post_to_x


class DailyState(TypedDict, total=False):
    input: str
    events: List[Dict[str, Any]]
    markets: List[Dict[str, Any]]
    analysis: str
    script: str
    video_path: str
    tweet_status: str
    output: str


def _utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _bool_env(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() == "true"


def _is_placeholder(value: Optional[str]) -> bool:
    if value is None:
        return True
    normalized = value.strip().lower()
    if not normalized:
        return True
    if normalized in {
        "your_openai_key_here",
        "your_api_key_here",
        "your_key_here",
        "your_token_here",
    }:
        return True
    if normalized.startswith("your_") and ("key" in normalized or "token" in normalized):
        return True
    if (normalized.startswith("<") and normalized.endswith(">")) or (
        normalized.startswith("[") and normalized.endswith("]")
    ) or (normalized.startswith("{") and normalized.endswith("}")):
        return True
    return False


def _first_env(*names: str) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value is None:
            continue
        if _is_placeholder(value):
            continue
        return value.strip()
    return None


def _compact_str(value: Any, limit: int = 240) -> Any:
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


def build_daily_graph() -> GraphAgent:
    raw_provider = _first_env("LLM_PROVIDER", "DEFAULT_LLM_PROVIDER") or "openai"
    provider = raw_provider.strip().lower()

    arcee_key = _first_env("ARCEE_AI_KEY", "ARCEE_API_KEY", "ARCEE_KEY", "Arcee_AI_KEY")
    if "arcee" in provider:
        provider = "openrouter"
        if arcee_key and not _first_env("OPENROUTER_API_KEY"):
            os.environ["OPENROUTER_API_KEY"] = arcee_key

    model_env_key = f"{provider.upper()}_MODEL"
    model_name = _first_env(model_env_key, "DEFAULT_MODEL") or "gpt-5.1-chat-latest"

    api_key = _first_env(f"{provider.upper()}_API_KEY")
    llm = ChatBot(
        llm_provider=provider,
        model_name=model_name,
        api_key=api_key,
    )

    async def fetch_node(state: DailyState) -> Dict[str, Any]:
        events = await fetch_events(
            limit=int(os.getenv("POLYMARKET_EVENTS_LIMIT", "25")),
            order=os.getenv("POLYMARKET_EVENTS_ORDER", "id"),
            ascending=os.getenv("POLYMARKET_EVENTS_ASC", "false").lower() == "true",
            closed=os.getenv("POLYMARKET_EVENTS_CLOSED", "false").lower() == "true",
        )
        markets = await fetch_markets(
            limit=int(os.getenv("POLYMARKET_MARKETS_LIMIT", "50")),
            order=os.getenv("POLYMARKET_MARKETS_ORDER", "volume"),
            ascending=os.getenv("POLYMARKET_MARKETS_ASC", "false").lower() == "true",
            active=os.getenv("POLYMARKET_MARKETS_ACTIVE", "true").lower() == "true",
        )
        slim_events = [_slim_event(event) for event in events]
        slim_markets = [_slim_market(market) for market in markets]
        return {"events": slim_events, "markets": slim_markets}

    async def analyze_node(state: DailyState) -> Dict[str, Any]:
        today = _utc_today()
        prompt = (
            "You are a market intelligence analyst. Summarize the most notable Polymarket "
            f"events and markets for {today}. Focus on: volume shifts, sentiment changes, "
            "newly active markets, and unresolved risks. Keep it factual and avoid giving "
            "investment advice. End with a clear disclaimer that this is not financial advice."
        )
        content = f"Events: {state.get('events', [])}\nMarkets: {state.get('markets', [])}"
        analysis = await llm.ask(
            [
                {"role": "system", "content": "You summarize prediction market data responsibly."},
                {"role": "user", "content": f"{prompt}\n\n{content}"},
            ]
        )
        return {"analysis": analysis}

    async def script_node(state: DailyState) -> Dict[str, Any]:
        today = _utc_today()
        prompt = (
            "Create a short (60-90 seconds) video script for a digital human. "
            f"Topic: Polymarket daily brief for {today}. "
            "Tone: confident, neutral, informative. "
            "Include a one-line disclaimer that this is not financial advice."
        )
        analysis = state.get("analysis", "")
        script = await llm.ask(
            [
                {"role": "system", "content": "You write concise scripts for short videos."},
                {"role": "user", "content": f"{prompt}\n\nReference summary:\n{analysis}"},
            ]
        )
        return {"script": script}

    async def video_node(state: DailyState) -> Dict[str, Any]:
        if not _bool_env("ENABLE_VIDEO_GENERATION", False):
            return {"video_path": "video_skipped"}
        script = state.get("script", "")
        video_path = generate_avatar_video(script=script, title="polymarket-daily")
        return {"video_path": video_path}

    async def tweet_node(state: DailyState) -> Dict[str, Any]:
        if not _bool_env("ENABLE_TWITTER_POST", False):
            return {"tweet_status": "tweet_skipped"}
        analysis = state.get("analysis", "")
        short_post = analysis[:260] + ("..." if len(analysis) > 260 else "")
        tweet_status = post_to_x(short_post, media_path=state.get("video_path"))
        return {"tweet_status": tweet_status}

    async def finalize_node(state: DailyState) -> Dict[str, Any]:
        output = state.get("analysis", "")
        return {"output": output}

    graph = StateGraph(DailyState)
    graph.add_node("fetch", fetch_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("script", script_node)
    graph.add_node("video", video_node)
    graph.add_node("tweet", tweet_node)
    graph.add_node("finalize", finalize_node)
    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "analyze")
    graph.add_edge("analyze", "script")
    graph.add_edge("script", "video")
    graph.add_edge("video", "tweet")
    graph.add_edge("tweet", "finalize")
    graph.add_edge("finalize", END)

    return GraphAgent(name="polymarket_daily_graph", graph=graph)
