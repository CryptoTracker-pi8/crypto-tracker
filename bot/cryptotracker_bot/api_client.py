import httpx
from cryptotracker_bot.config import get_settings
from typing import Any, Dict, List


class APIClient:
    """
    Client for interacting with the backend API.
    """

    def __init__(self, tg_user_id: str | None = None):
        self.settings = get_settings()
        self.base_url = self.settings.API_BASE_URL
        self._headers = {"X-Telegram-ID": str(tg_user_id)} if tg_user_id else {}

    async def get_currency(self, symbol: str) -> dict | None:
        """
        Get currency details by symbol.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/currencies/{symbol.upper()}",
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("currency")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise
            except Exception as e:
                print(f"Error fetching currency: {e}")
                return None

    async def get_portfolio(self) -> Dict[str, Any]:
        """
        Get user portfolio by X-Telegram-ID
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/portfolio", headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def get_favorites(self) -> List[Dict[str, Any]]:
        """
        Get user favorites by X-Telegram-ID
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/favorites", headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def get_portfolio_stats(self) -> Dict[str, Any]:
        """
        Get user portfolio stats
        """
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            r = await client.get("/portfolio/stats", headers=self._headers)
            r.raise_for_status()
            return r.json()


api_client = APIClient()

