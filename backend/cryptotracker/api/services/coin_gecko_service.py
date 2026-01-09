from datetime import datetime, timedelta
from typing import Optional

import httpx
from aiocache import Cache
from aiocache.serializers import PickleSerializer

from cryptotracker.api.schemas.currencies_schemas import CurrencyHistoryPoint, CurrencyPrice
from cryptotracker.domains.currencies.repository import CoinGeckoRepository


class CoinGeckoService:
    def __init__(self):
        self.repository = CoinGeckoRepository()
        self.cache = Cache(Cache.MEMORY, serializer=PickleSerializer())
        self.short_ttl = 300  # 5 минут для быстро меняющихся данных (цены)
        self.long_ttl = 300  # 5 минут для стабильных данных (история, детали)
        self.stale_ttl = 86400  # 24 часа для устаревшего кеша при ошибках API

    async def get_popular_currencies(self, limit: int = 50) -> list[CurrencyPrice]:
        cache_key = f"currencies:popular:{limit}"
        stale_key = f"currencies:popular:{limit}:stale"
        cached = await self.cache.get(cache_key)

        if cached:
            return cached

        try:
            data = await self.repository.fetch_markets(limit=limit, page=1)
        except httpx.HTTPStatusError:
            stale = await self.cache.get(stale_key)
            if stale:
                return stale
            raise

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

        await self.cache.set(cache_key, result, ttl=self.short_ttl)
        await self.cache.set(stale_key, result, ttl=self.stale_ttl)
        return result

    async def get_currency_by_symbol(self, symbol: str) -> Optional[CurrencyPrice]:
        cache_key = f"currency:{symbol.upper()}"
        stale_key = f"currency:{symbol.upper()}:stale"
        cached = await self.cache.get(cache_key)

        if cached:
            return cached

        coin_id = await self._get_coin_id_by_symbol(symbol)

        if not coin_id:
            return None

        try:
            data = await self.repository.fetch_coin_details(coin_id)
        except httpx.HTTPStatusError:
            stale = await self.cache.get(stale_key)
            if stale:
                return stale
            raise
        market_data = data.get("market_data", {})

        result = CurrencyPrice(
            symbol=symbol.upper(),
            name=data["name"],
            price_usd=market_data.get("current_price", {}).get("usd", 0),
            price_change_24h=market_data.get("price_change_percentage_24h"),
            market_cap=market_data.get("market_cap", {}).get("usd"),
            volume_24h=market_data.get("total_volume", {}).get("usd"),
        )

        await self.cache.set(cache_key, result, ttl=self.short_ttl)
        await self.cache.set(stale_key, result, ttl=self.stale_ttl)
        return result

    async def get_currency_history(self, symbol: str, days: int = 7) -> list[CurrencyHistoryPoint]:
        base_days = 90
        requested_days = min(days, base_days)
        cache_key = f"currency:history:{symbol.upper()}:{requested_days}"
        base_cache_key = f"currency:history:{symbol.upper()}:{base_days}"
        stale_key = f"currency:history:{symbol.upper()}:{requested_days}:stale"
        cached = await self.cache.get(cache_key)

        if cached:
            return cached

        base_cached = await self.cache.get(base_cache_key)
        if base_cached:
            if requested_days >= base_days:
                return base_cached
            cutoff = datetime.utcnow() - timedelta(days=requested_days)
            result = [point for point in base_cached if point.timestamp >= cutoff]
            await self.cache.set(cache_key, result, ttl=self.long_ttl)
            await self.cache.set(stale_key, result, ttl=self.stale_ttl)
            return result

        coin_id = await self._get_coin_id_by_symbol(symbol)

        if not coin_id:
            return []

        try:
            data = await self.repository.fetch_market_chart(coin_id, base_days)
        except httpx.HTTPStatusError:
            stale = await self.cache.get(stale_key)
            if stale:
                return stale
            raise
        prices = data.get("prices", [])

        full_history = [
            CurrencyHistoryPoint(
                timestamp=datetime.fromtimestamp(price[0] / 1000),
                price=price[1],
            )
            for price in prices
        ]

        await self.cache.set(base_cache_key, full_history, ttl=self.long_ttl)
        await self.cache.set(f"{base_cache_key}:stale", full_history, ttl=self.stale_ttl)

        if requested_days >= base_days:
            await self.cache.set(cache_key, full_history, ttl=self.long_ttl)
            await self.cache.set(stale_key, full_history, ttl=self.stale_ttl)
            return full_history

        cutoff = datetime.utcnow() - timedelta(days=requested_days)
        result = [point for point in full_history if point.timestamp >= cutoff]

        await self.cache.set(cache_key, result, ttl=self.long_ttl)
        await self.cache.set(stale_key, result, ttl=self.stale_ttl)
        return result

    async def _get_coin_id_by_symbol(self, symbol: str) -> Optional[str]:
        """Получить coin_id по символу с кешированием"""
        cache_key = f"coin_id:{symbol.upper()}"
        markets_key = "markets:all"
        cached = await self.cache.get(cache_key)

        if cached:
            return cached

        markets_cached = await self.cache.get(markets_key)
        if markets_cached:
            for coin in markets_cached:
                if coin["symbol"].upper() == symbol.upper():
                    coin_id = coin["id"]
                    await self.cache.set(cache_key, coin_id, ttl=self.long_ttl)
                    return coin_id

        try:
            coins = await self.repository.fetch_markets(limit=250, page=1)
        except httpx.HTTPStatusError:
            if markets_cached:
                for coin in markets_cached:
                    if coin["symbol"].upper() == symbol.upper():
                        coin_id = coin["id"]
                        await self.cache.set(cache_key, coin_id, ttl=self.long_ttl)
                        return coin_id
            raise
        await self.cache.set(markets_key, coins, ttl=self.long_ttl)

        coin_id = None
        for coin in coins:
            if coin["symbol"].upper() == symbol.upper():
                coin_id = coin["id"]
                break

        if coin_id:
            await self.cache.set(cache_key, coin_id, ttl=self.long_ttl)

        return coin_id
