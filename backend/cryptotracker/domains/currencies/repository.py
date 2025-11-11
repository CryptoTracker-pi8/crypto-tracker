import httpx


class CoinGeckoRepository:
    BASE_URL = "https://api.coingecko.com/api/v3"

    async def fetch_markets(self, limit: int, page: int = 1) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": limit,
                    "page": page,
                    "sparkline": False,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def fetch_coin_details(self, coin_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/coins/{coin_id}",
                params={
                    "localization": False,
                    "tickers": False,
                    "market_data": True,
                    "community_data": False,
                    "developer_data": False
                },
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def fetch_market_chart(self, coin_id: str, days: int) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": days},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
