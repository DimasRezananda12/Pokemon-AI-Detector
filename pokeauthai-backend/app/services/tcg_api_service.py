import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx

from app.config import get_settings
from app.models.schemas import Card
from app.services.cache_manager import cache_manager

_LOGGER = logging.getLogger("pokeauthai.tcg_api")


@asynccontextmanager
async def get_tcg_api_client(
    client: httpx.AsyncClient | None = None,
) -> AsyncIterator[httpx.AsyncClient]:
    if client is not None:
        yield client
        return

    settings = get_settings()
    headers: dict[str, str] = {}
    if settings.pokemon_tcg_api_key:
        headers["X-Api-Key"] = settings.pokemon_tcg_api_key

    async with httpx.AsyncClient(
        base_url=settings.pokemon_tcg_api_base_url,
        timeout=settings.pokemon_tcg_api_timeout_seconds,
        headers=headers,
    ) as created_client:
        yield created_client


def _parse_hp(hp_str: str | None) -> int | None:
    if not hp_str:
        return None
    try:
        # Some HPs can have words or symbols, keeping it simple
        return int("".join(filter(str.isdigit, hp_str)))
    except ValueError:
        return None


def _normalize_card(card_payload: dict[str, Any]) -> Card:
    set_payload = card_payload.get("set") or {}
    images_payload = card_payload.get("images") or {}

    hp = _parse_hp(card_payload.get("hp"))

    return Card(
        id=str(card_payload.get("id") or ""),
        name=str(card_payload.get("name") or ""),
        set_name=set_payload.get("name"),
        set_code=set_payload.get("id"),
        hp=hp,
        types=card_payload.get("types") or [],
        rarity=card_payload.get("rarity"),
        image_url=images_payload.get("large") or images_payload.get("small"),
        card_number=str(card_payload.get("number")) if card_payload.get("number") is not None else None,
        language="en",  # TCG API v2 is primarily English
    )


async def search_card(
    name: str,
    set_filter: str | None = None,
    client: httpx.AsyncClient | None = None,
) -> Card | None:
    settings = get_settings()
    
    # Try cache first (key by name and set_filter)
    cache_key = f"search_{name}_{set_filter or 'any'}"
    cached_data = cache_manager.get("tcg_cards", cache_key, ttl_seconds=settings.cache_ttl)
    if cached_data:
        return Card(**cached_data)

    query = f'name:"{name}"'
    if set_filter:
        query += f' set.id:"{set_filter}" OR set.name:"{set_filter}"'

    try:
        async with get_tcg_api_client(client=client) as resolved_client:
            response = await resolved_client.get("/cards", params={"q": query, "pageSize": 10})
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as e:
        _LOGGER.error(f"Error searching card '{name}': {e}")
        return None

    cards = payload.get("data") or []
    if not cards:
        return None

    # For fuzzy matching, we take the first exact name match, or just the first result
    best_match = None
    for card_payload in cards:
        if card_payload.get("name", "").lower() == name.lower():
            best_match = card_payload
            break
            
    if not best_match:
        best_match = cards[0]
        
    card = _normalize_card(best_match)
    
    # Cache result
    cache_manager.set("tcg_cards", cache_key, card.model_dump())
    
    return card


async def get_card_by_id(
    card_id: str,
    client: httpx.AsyncClient | None = None,
) -> Card | None:
    settings = get_settings()
    
    # Try cache
    cache_key = f"id_{card_id}"
    cached_data = cache_manager.get("tcg_cards", cache_key, ttl_seconds=settings.cache_ttl)
    if cached_data:
        return Card(**cached_data)

    try:
        async with get_tcg_api_client(client=client) as resolved_client:
            response = await resolved_client.get(f"/cards/{card_id}")
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as e:
        _LOGGER.error(f"Error getting card ID '{card_id}': {e}")
        return None

    card_payload = payload.get("data")
    if not isinstance(card_payload, dict):
        return None
        
    card = _normalize_card(card_payload)
    
    # Cache result
    cache_manager.set("tcg_cards", cache_key, card.model_dump())
    
    return card


async def get_official_image_url(card_id: str) -> str | None:
    card = await get_card_by_id(card_id)
    if card:
        return card.image_url
    return None
