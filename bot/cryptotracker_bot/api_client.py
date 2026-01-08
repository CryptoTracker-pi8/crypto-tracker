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
            try:
                r = await client.get(f"{self.base_url}/portfolio", headers=self._headers)
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise

    async def get_favorites(self) -> List[Dict[str, Any]]:
        """
        Get user favorites by X-Telegram-ID
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/favorites", headers=self._headers)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict):
                return data.get("favorites", [])
            return data

    async def add_favorite(self, symbol: str) -> Dict[str, Any]:
        """
        Add currency to favorites.
        """
        payload = {"currency_symbol": symbol.upper()}
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{self.base_url}/favorites", headers=self._headers, json=payload)
            r.raise_for_status()
            return r.json()

    async def delete_favorite(self, symbol: str) -> Dict[str, Any]:
        """
        Remove currency from favorites.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.delete(f"{self.base_url}/favorites/{symbol.upper()}", headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def get_portfolio_stats(self) -> Dict[str, Any]:
        """
        Get user portfolio stats
        """
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            try:
                r = await client.get("/portfolio/stats", headers=self._headers)
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise

    async def list_alerts(self) -> List[Dict[str, Any]]:
        """
        Get user alerts.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/alerts", headers=self._headers)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict):
                return data.get("alerts", [])
            return data

    async def create_alert(self, symbol: str, percent: str, direction: str = "both") -> Dict[str, Any]:
        """
        Create new alert.
        """
        payload = {
            "symbol": symbol.upper(),
            "percent": percent,
            "direction": direction,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.post(f"{self.base_url}/alerts", headers=self._headers, json=payload)
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError as e:
                detail = None
                try:
                    data = e.response.json()
                    if isinstance(data, dict):
                        detail = data.get("detail")
                except Exception:
                    detail = e.response.text
                raise ValueError(detail or str(e))

    async def delete_alert(self, alert_id: int) -> Dict[str, Any]:
        """
        Delete alert by id.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.delete(f"{self.base_url}/alerts/{alert_id}", headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def get_settings(self) -> Dict[str, Any]:
        """
        Get current user settings.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/settings", headers=self._headers)
            r.raise_for_status()
            return r.json()

    async def update_settings(
        self,
        theme: str | None = None,
        notification_mode: str | None = None,
    ) -> Dict[str, Any]:
        """
        Update current user settings.
        """
        payload: Dict[str, Any] = {}
        if theme is not None:
            payload["theme"] = theme
        if notification_mode is not None:
            payload["notification_mode"] = notification_mode

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.put(f"{self.base_url}/settings", headers=self._headers, json=payload)
            r.raise_for_status()
            return r.json()


api_client = APIClient()
