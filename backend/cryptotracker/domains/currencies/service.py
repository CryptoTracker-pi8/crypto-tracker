from datetime import datetime
from typing import Optional

import httpx

from cryptotracker.domains.currencies.schemas import CurrencyHistoryPoint, CurrencyPrice


class CoinGeckoService:
    """
    Service for interacting with CoinGecko API.
    """
    BASE_URL = "https://api.coingecko.com/api/v3"

    async def get_popular_currencies(self, limit: int = 50) -> list[CurrencyPrice]:
        """
        Get list of popular cryptocurrencies.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": limit,
                    "page": 1,
                    "sparkline": False,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            return [
                CurrencyPrice(
                    symbol=item["symbol"].upper(),
                    name=item["name"],
                    price_usd=item.get("current_price", 0) or 0,
                    price_change_24h=item.get("price_change_percentage_24h"),
                    market_cap=item.get("market_cap"),
                    volume_24h=item.get("total_volume"),
                )
                for item in data
            ]

    async def get_currency_by_symbol(self, symbol: str) -> Optional[CurrencyPrice]:
        """
        Get currency details by symbol.
        Prioritizes coins by market cap when multiple coins share the same symbol.
        """
        # CoinGecko uses coin IDs, not symbols, so we need to search
        async with httpx.AsyncClient() as client:
            # First, get list of coins with highest market cap (top 250)
            response = await client.get(
                f"{self.BASE_URL}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 250,
                    "page": 1,
                    "sparkline": False,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            coins = response.json()

            # Find the coin with matching symbol (prioritized by market cap)
            coin_id = None
            for coin in coins:
                if coin["symbol"].upper() == symbol.upper():
                    coin_id = coin["id"]
                    break

            if not coin_id:
                return None

            # Get coin details
            response = await client.get(
                f"{self.BASE_URL}/coins/{coin_id}",
                params={"localization": False, "tickers": False, "market_data": True, "community_data": False, "developer_data": False},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            market_data = data.get("market_data", {})

            return CurrencyPrice(
                symbol=symbol.upper(),
                name=data["name"],
                price_usd=market_data.get("current_price", {}).get("usd", 0),
                price_change_24h=market_data.get("price_change_percentage_24h"),
                market_cap=market_data.get("market_cap", {}).get("usd"),
                volume_24h=market_data.get("total_volume", {}).get("usd"),
            )

    async def get_currency_history(self, symbol: str, days: int = 7) -> list[CurrencyHistoryPoint]:
        """
        Get currency price history.
        """
        async with httpx.AsyncClient() as client:
            # Get coin ID by symbol
            response = await client.get(
                f"{self.BASE_URL}/coins/list",
                params={"include_platform": False},
                timeout=10.0,
            )
            response.raise_for_status()
            coins = response.json()

            coin_id = None
            for coin in coins:
                if coin["symbol"].upper() == symbol.upper():
                    coin_id = coin["id"]
                    break

            if not coin_id:
                return []

            # Get price history
            response = await client.get(
                f"{self.BASE_URL}/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": days},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            prices = data.get("prices", [])
            return [
                CurrencyHistoryPoint(
                    timestamp=datetime.fromtimestamp(price[0] / 1000),
                    price=price[1],
                )
                for price in prices
            ]

