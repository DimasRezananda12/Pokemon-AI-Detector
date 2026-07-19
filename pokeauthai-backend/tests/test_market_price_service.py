"""
Tests for market_price_service.py
Uses mock HTTP responses to avoid real API calls.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.market_price_service import (
    fetch_market_prices,
    _parse_tcgplayer_prices,
    _parse_cardmarket_prices,
    _build_unavailable,
    PriceData,
)


# --- Unit tests for parsing functions ---

def test_parse_tcgplayer_prices_normal():
    data = {
        "url": "https://prices.pokemontcg.io/tcgplayer/base1-4",
        "prices": {
            "holofoil": {
                "low": 150.0,
                "mid": 250.0,
                "high": 500.0,
                "market": 220.0,
            }
        },
    }
    result = _parse_tcgplayer_prices(data)
    assert result.source == "tcgplayer"
    assert result.currency == "USD"
    assert result.low == 150.0
    assert result.mid == 250.0
    assert result.high == 500.0
    assert result.market == 220.0
    assert result.status == "available"
    assert "tcgplayer" in result.url


def test_parse_tcgplayer_prices_no_prices():
    data = {"url": "https://example.com", "prices": {}}
    result = _parse_tcgplayer_prices(data)
    assert result.status == "no_price_data"


def test_parse_cardmarket_prices():
    data = {
        "url": "https://prices.pokemontcg.io/cardmarket/base1-4",
        "prices": {
            "lowPrice": 80.0,
            "averageSellPrice": 120.0,
            "trendPrice": 150.0,
            "avg1": 110.0,
        },
    }
    result = _parse_cardmarket_prices(data)
    assert result.source == "cardmarket"
    assert result.currency == "EUR"
    assert result.low == 80.0
    assert result.mid == 120.0
    assert result.high == 150.0
    assert result.market == 120.0
    assert result.status == "available"


def test_build_unavailable():
    result = _build_unavailable()
    assert result.status == "unavailable"
    assert result.low is None
    assert result.market is None


# --- Integration test for fetch_market_prices ---

@pytest.mark.asyncio
async def test_fetch_market_prices_success():
    """Test successful fetch with mocked HTTP response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "id": "base1-4",
            "name": "Charizard",
            "tcgplayer": {
                "url": "https://prices.pokemontcg.io/tcgplayer/base1-4",
                "prices": {
                    "holofoil": {
                        "low": 150.0,
                        "mid": 250.0,
                        "high": 500.0,
                        "market": 220.0,
                    }
                },
            },
            "cardmarket": {
                "url": "https://prices.pokemontcg.io/cardmarket/base1-4",
                "prices": {
                    "lowPrice": 80.0,
                    "averageSellPrice": 120.0,
                    "trendPrice": 150.0,
                },
            },
        }
    }

    with patch("app.services.market_price_service.httpx.AsyncClient") as MockClient, \
         patch("app.services.market_price_service.cache_manager") as mock_cache:

        mock_cache.get.return_value = None  # No cache hit

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client_instance

        results = await fetch_market_prices("base1-4")

    assert len(results) == 2
    tcg = [r for r in results if r.source == "tcgplayer"][0]
    cm = [r for r in results if r.source == "cardmarket"][0]

    assert tcg.low == 150.0
    assert tcg.market == 220.0
    assert cm.low == 80.0
    assert cm.market == 120.0


@pytest.mark.asyncio
async def test_fetch_market_prices_api_down_fallback():
    """Test fallback when API is unreachable."""
    import httpx as real_httpx

    with patch("app.services.market_price_service.httpx.AsyncClient") as MockClient, \
         patch("app.services.market_price_service.cache_manager") as mock_cache:

        mock_cache.get.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = real_httpx.ConnectError("Connection refused")
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client_instance

        results = await fetch_market_prices("base1-4")

    assert len(results) == 1
    assert results[0].status == "unavailable"


@pytest.mark.asyncio
async def test_fetch_market_prices_cache_hit():
    """Test that cached prices are returned without API call."""
    cached_data = [
        {
            "source": "tcgplayer", "currency": "USD",
            "low": 100.0, "mid": 150.0, "high": 200.0, "market": 140.0,
            "url": "https://example.com", "status": "available",
        }
    ]

    with patch("app.services.market_price_service.cache_manager") as mock_cache:
        mock_cache.get.return_value = cached_data

        results = await fetch_market_prices("base1-4")

    assert len(results) == 1
    assert results[0].source == "tcgplayer"
    assert results[0].market == 140.0
