import httpx
from cryptotracker_bot.config import get_settings


class APIClient:
    """
    Client for interacting with the backend API.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.API_BASE_URL
    
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


api_client = APIClient()

