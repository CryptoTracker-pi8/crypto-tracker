from datetime import datetime

import httpx
from fastapi.testclient import TestClient

from cryptotracker.__main__ import get_app
from cryptotracker.api.endpoints import currencies
from cryptotracker.api.schemas.currencies_schemas import CurrencyHistoryPoint, CurrencyPrice


def test_get_currencies_success():
    app = get_app()
    client = TestClient(app)

    async def get_popular_currencies(limit: int = 50):
        return [
            CurrencyPrice(
                symbol="BTC",
                name="Bitcoin",
                price_usd=100.0,
                price_change_24h=1.2,
                market_cap=1000.0,
                volume_24h=10.0,
            )
        ]

    currencies.coin_gecko_service.get_popular_currencies = get_popular_currencies  # type: ignore[assignment]

    response = client.get("/api/v1/currencies", params={"limit": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["currencies"][0]["symbol"] == "BTC"


def test_get_currency_not_found():
    app = get_app()
    client = TestClient(app)

    async def get_currency_by_symbol(symbol: str):
        return None

    currencies.coin_gecko_service.get_currency_by_symbol = get_currency_by_symbol  # type: ignore[assignment]

    response = client.get("/api/v1/currencies/abc")
    assert response.status_code == 404


def test_get_currency_502_on_http_error():
    app = get_app()
    client = TestClient(app)

    async def get_currency_by_symbol(symbol: str):
        request = httpx.Request("GET", "https://api.coingecko.com/api/v3/coins/bitcoin")
        response = httpx.Response(429, request=request, text="rate limit")
        raise httpx.HTTPStatusError("rate limit", request=request, response=response)

    currencies.coin_gecko_service.get_currency_by_symbol = get_currency_by_symbol  # type: ignore[assignment]

    response = client.get("/api/v1/currencies/btc")
    assert response.status_code == 502


def test_get_history_not_found():
    app = get_app()
    client = TestClient(app)

    async def get_currency_history(symbol: str, days: int = 7):
        return []

    currencies.coin_gecko_service.get_currency_history = get_currency_history  # type: ignore[assignment]

    response = client.get("/api/v1/currencies/btc/history", params={"days": 7})
    assert response.status_code == 404


def test_get_history_success():
    app = get_app()
    client = TestClient(app)

    async def get_currency_history(symbol: str, days: int = 7):
        return [CurrencyHistoryPoint(timestamp=datetime(2024, 1, 1), price=100.0)]

    currencies.coin_gecko_service.get_currency_history = get_currency_history  # type: ignore[assignment]

    response = client.get("/api/v1/currencies/btc/history", params={"days": 7})
    assert response.status_code == 200
    body = response.json()
    assert body["history"][0]["price"] == 100.0
