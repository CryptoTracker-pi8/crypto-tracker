from datetime import datetime, timedelta

import httpx
import pytest

from cryptotracker.api.schemas.currencies_schemas import CurrencyHistoryPoint, CurrencyPrice
from cryptotracker.api.services.coin_gecko_service import CoinGeckoService


@pytest.mark.asyncio
async def test_get_currency_by_symbol_uses_cache():
    service = CoinGeckoService()
    calls = {"markets": 0, "details": 0}

    async def fetch_markets(limit: int, page: int = 1):
        calls["markets"] += 1
        return [{"id": "bitcoin", "symbol": "btc"}]

    async def fetch_coin_details(coin_id: str):
        calls["details"] += 1
        assert coin_id == "bitcoin"
        return {
            "name": "Bitcoin",
            "market_data": {
                "current_price": {"usd": 100.0},
                "price_change_percentage_24h": 1.5,
                "market_cap": {"usd": 500.0},
                "total_volume": {"usd": 50.0},
            },
        }

    service.repository.fetch_markets = fetch_markets  # type: ignore[assignment]
    service.repository.fetch_coin_details = fetch_coin_details  # type: ignore[assignment]

    first = await service.get_currency_by_symbol("BTC")
    second = await service.get_currency_by_symbol("BTC")

    assert first is not None
    assert second is not None
    assert first.price_usd == 100.0
    assert calls["details"] == 1


@pytest.mark.asyncio
async def test_get_currency_by_symbol_uses_stale_cache_on_http_error():
    service = CoinGeckoService()
    stale_currency = CurrencyPrice(
        symbol="BTC",
        name="Bitcoin",
        price_usd=123.0,
        price_change_24h=1.2,
        market_cap=1000.0,
        volume_24h=10.0,
    )
    await service.cache.set("currency:BTC:stale", stale_currency, ttl=service.stale_ttl)

    async def fetch_markets(limit: int, page: int = 1):
        return [{"id": "bitcoin", "symbol": "btc"}]

    async def fetch_coin_details(coin_id: str):
        request = httpx.Request("GET", "https://api.coingecko.com/api/v3/coins/bitcoin")
        response = httpx.Response(429, request=request, text="rate limit")
        raise httpx.HTTPStatusError("rate limit", request=request, response=response)

    service.repository.fetch_markets = fetch_markets  # type: ignore[assignment]
    service.repository.fetch_coin_details = fetch_coin_details  # type: ignore[assignment]

    result = await service.get_currency_by_symbol("BTC")
    assert result is not None
    assert result.price_usd == 123.0


@pytest.mark.asyncio
async def test_get_popular_currencies_cached():
    service = CoinGeckoService()
    calls = {"markets": 0}

    async def fetch_markets(limit: int, page: int = 1):
        calls["markets"] += 1
        return [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 100.0,
                "price_change_percentage_24h": 1.5,
                "market_cap": 500.0,
                "total_volume": 50.0,
            }
        ]

    service.repository.fetch_markets = fetch_markets  # type: ignore[assignment]

    first = await service.get_popular_currencies(limit=1)
    second = await service.get_popular_currencies(limit=1)

    assert len(first) == 1
    assert len(second) == 1
    assert calls["markets"] == 1


@pytest.mark.asyncio
async def test_get_currency_history_fetches_90_days_and_slices():
    service = CoinGeckoService()
    calls = {"markets": 0, "history": 0}

    async def fetch_markets(limit: int, page: int = 1):
        calls["markets"] += 1
        return [{"id": "bitcoin", "symbol": "btc"}]

    async def fetch_market_chart(coin_id: str, days: int):
        calls["history"] += 1
        assert days == 90
        now = datetime.utcnow()
        prices = []
        for day in range(90):
            ts = now - timedelta(days=day)
            prices.append([int(ts.timestamp() * 1000), 100 + day])
        return {"prices": prices}

    service.repository.fetch_markets = fetch_markets  # type: ignore[assignment]
    service.repository.fetch_market_chart = fetch_market_chart  # type: ignore[assignment]

    history_7 = await service.get_currency_history("BTC", days=7)
    history_30 = await service.get_currency_history("BTC", days=30)

    assert calls["history"] == 1
    assert 7 <= len(history_7) <= 8
    assert len(history_30) >= len(history_7)


@pytest.mark.asyncio
async def test_get_currency_history_uses_cached_base_history():
    service = CoinGeckoService()
    now = datetime.utcnow()
    base_history = [
        CurrencyHistoryPoint(timestamp=now - timedelta(days=day), price=100 + day)
        for day in range(90)
    ]
    await service.cache.set("currency:history:BTC:90", base_history, ttl=service.long_ttl)

    history_7 = await service.get_currency_history("BTC", days=7)
    assert 7 <= len(history_7) <= 8
