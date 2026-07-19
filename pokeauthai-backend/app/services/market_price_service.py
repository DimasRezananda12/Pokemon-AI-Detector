"""
Market Price Service — fetches real pricing data from Pokemon TCG API
(which includes TCGPlayer pricing) with 6-hour cache TTL.

Cardmarket API requires OAuth 1.0a credentials which most users won't have,
so we use the Pokemon TCG API's built-in tcgplayer pricing as the primary source
and provide a Cardmarket stub that activates when credentials are available.

Fallback: If API is down or card not found, returns mock/unavailable pricing.
"""
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import get_settings
from app.services.cache_manager import cache_manager
from app.services import tcg_api_service

_LOGGER = logging.getLogger("pokeauthai.market_price")

MARKET_CACHE_TTL = 21600  # 6 hours in seconds


@dataclass
class PriceData:
    source: str
    currency: str
    low: float | None = None
    mid: float | None = None
    high: float | None = None
    market: float | None = None
    url: str | None = None
    status: str = "available"


def _build_unavailable(source: str = "tcgplayer") -> PriceData:
    return PriceData(
        source=source,
        currency="USD",
        status="unavailable",
    )


def _parse_tcgplayer_prices(tcgplayer_data: dict[str, Any]) -> PriceData:
    """Parse TCGPlayer pricing from the Pokemon TCG API response."""
    url = tcgplayer_data.get("url")
    prices = tcgplayer_data.get("prices", {})

    # TCGPlayer has multiple price tiers: normal, holofoil, reverseHolofoil, etc.
    # Pick the first available tier.
    best_tier = None
    for tier_name in ["normal", "holofoil", "reverseHolofoil", "1stEditionHolofoil", "1stEditionNormal"]:
        if tier_name in prices and prices[tier_name]:
            best_tier = prices[tier_name]
            break

    if not best_tier:
        # Try any available key
        for key, value in prices.items():
            if isinstance(value, dict) and value:
                best_tier = value
                break

    if not best_tier:
        return PriceData(
            source="tcgplayer",
            currency="USD",
            url=url,
            status="no_price_data",
        )

    return PriceData(
        source="tcgplayer",
        currency="USD",
        low=best_tier.get("low"),
        mid=best_tier.get("mid"),
        high=best_tier.get("high"),
        market=best_tier.get("market"),
        url=url,
        status="available",
    )


def _parse_cardmarket_prices(cardmarket_data: dict[str, Any]) -> PriceData:
    """Parse Cardmarket pricing from the Pokemon TCG API response."""
    url = cardmarket_data.get("url")
    prices = cardmarket_data.get("prices", {})

    if not prices:
        return PriceData(
            source="cardmarket",
            currency="EUR",
            url=url,
            status="no_price_data",
        )

    return PriceData(
        source="cardmarket",
        currency="EUR",
        low=prices.get("lowPrice"),
        mid=prices.get("averageSellPrice") or prices.get("avg1"),
        high=prices.get("trendPrice"),
        market=prices.get("averageSellPrice"),
        url=url,
        status="available",
    )


async def fetch_market_prices(card_id: str) -> list[PriceData]:
    """
    Fetch market prices for a card. Uses Pokemon TCG API which embeds
    both TCGPlayer and Cardmarket pricing data.

    Returns a list of PriceData (one per source).
    Cache: 6-hour TTL.
    Fallback: returns mock if API is down.
    """
    # --- Check cache ---
    cache_key = f"market_{card_id}"
    cached = cache_manager.get("market_prices", cache_key, ttl_seconds=MARKET_CACHE_TTL)
    if cached:
        _LOGGER.debug(f"Cache hit for market prices: {card_id}")
        return [PriceData(**p) for p in cached]

    # --- Fetch from API ---
    settings = get_settings()
    results: list[PriceData] = []

    try:
        headers: dict[str, str] = {}
        if settings.pokemon_tcg_api_key:
            headers["X-Api-Key"] = settings.pokemon_tcg_api_key

        async with httpx.AsyncClient(
            base_url=settings.pokemon_tcg_api_base_url,
            timeout=settings.pokemon_tcg_api_timeout_seconds,
            headers=headers,
        ) as client:
            response = await client.get(f"/cards/{card_id}")
            response.raise_for_status()
            payload = response.json()

        card_data = payload.get("data", {})

        # --- Parse TCGPlayer ---
        tcgplayer_data = card_data.get("tcgplayer")
        if tcgplayer_data:
            results.append(_parse_tcgplayer_prices(tcgplayer_data))

        # --- Parse Cardmarket ---
        cardmarket_data = card_data.get("cardmarket")
        if cardmarket_data:
            results.append(_parse_cardmarket_prices(cardmarket_data))

    except (httpx.HTTPError, ValueError, KeyError) as e:
        _LOGGER.warning(f"Market price fetch failed for {card_id}: {e}")

    # --- Fallback ---
    if not results:
        _LOGGER.info(f"No market data available for {card_id}, returning unavailable.")
        results.append(_build_unavailable())

    # --- Cache results ---
    cache_manager.set(
        "market_prices",
        cache_key,
        [{"source": p.source, "currency": p.currency, "low": p.low,
          "mid": p.mid, "high": p.high, "market": p.market,
          "url": p.url, "status": p.status} for p in results],
    )

    return results
