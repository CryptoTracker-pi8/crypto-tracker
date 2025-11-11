from datetime import datetime
from typing import Optional

from aiocache import Cache
from aiocache.serializers import PickleSerializer

from backend.cryptotracker.api.schemas.currencies_schemas import CurrencyHistoryPoint, CurrencyPrice
from cryptotracker.domains.currencies.repository import CoinGeckoRepository


class CoinGeckoService:
    def __init__(self):
        self.repository = CoinGeckoRepository()
        self.cache = Cache(Cache.MEMORY, serializer=PickleSerializer(), ttl=60)

    async def get_popular_currencies(self, limit: int = 50) -> list[CurrencyPrice]:
        cache_key = f"currencies:popular:{limit}"
        cached = await self.cache.get(cache_key)

        if cached:
            return cached

        data = await self.repository.fetch_markets(limit=limit, page=1)

        result = [
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

        await self.cache.set(cache_key, result)
        return result

    async def get_currency_by_symbol(self, symbol: str) -> Optional[CurrencyPrice]:
        cache_key = f"currency:{symbol.upper()}"
        cached = await self.cache.get(cache_key)

        if cached:
            return cached

        coins = await self.repository.fetch_markets(limit=250, page=1)

        coin_id = None
        for coin in coins:
            if coin["symbol"].upper() == symbol.upper():
                coin_id = coin["id"]
                break

        if not coin_id:
            return None

        data = await self.repository.fetch_coin_details(coin_id)
        market_data = data.get("market_data", {})

        result = CurrencyPrice(
            symbol=symbol.upper(),
            name=data["name"],
            price_usd=market_data.get("current_price", {}).get("usd", 0),
            price_change_24h=market_data.get("price_change_percentage_24h"),
            market_cap=market_data.get("market_cap", {}).get("usd"),
            volume_24h=market_data.get("total_volume", {}).get("usd"),
        )

        await self.cache.set(cache_key, result)
        return result

    async def get_currency_history(self, symbol: str, days: int = 7) -> list[CurrencyHistoryPoint]:
        coins = await self.repository.fetch_markets(limit=250, page=1)

        coin_id = None
        for coin in coins:
            if coin["symbol"].upper() == symbol.upper():
                coin_id = coin["id"]
                break

        if not coin_id:
            return []

        data = await self.repository.fetch_market_chart(coin_id, days)
        prices = data.get("prices", [])

        return [
            CurrencyHistoryPoint(
                timestamp=datetime.fromtimestamp(price[0] / 1000),
                price=price[1],
            )
            for price in prices
        ]


