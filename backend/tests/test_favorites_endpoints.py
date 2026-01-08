from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from cryptotracker.__main__ import get_app
from cryptotracker.api.endpoints import favorites
from cryptotracker.utils import auth


def _override_user():
    return SimpleNamespace(id=1, telegram_id=123)


def test_create_favorite_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    created = SimpleNamespace(id=10, currency_symbol="BTC", created_at=datetime(2024, 1, 1))

    async def create_favorite(db, user_id: int, currency_symbol: str):
        assert user_id == 1
        assert currency_symbol == "BTC"
        return created

    favorites.favorites_service.create_favorite = create_favorite  # type: ignore[assignment]

    response = client.post("/api/v1/favorites", json={"currency_symbol": "BTC"})
    assert response.status_code == 201
    assert response.json()["currency_symbol"] == "BTC"


def test_create_favorite_duplicate():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def create_favorite(db, user_id: int, currency_symbol: str):
        raise ValueError("Currency BTC is already in favorites")

    favorites.favorites_service.create_favorite = create_favorite  # type: ignore[assignment]

    response = client.post("/api/v1/favorites", json={"currency_symbol": "BTC"})
    assert response.status_code == 400


def test_get_favorites_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    favorites_list = [
        SimpleNamespace(id=1, currency_symbol="BTC", created_at=datetime(2024, 1, 1)),
        SimpleNamespace(id=2, currency_symbol="ETH", created_at=datetime(2024, 1, 2)),
    ]

    async def get_user_favorites(db, user_id: int):
        assert user_id == 1
        return favorites_list

    favorites.favorites_service.get_user_favorites = get_user_favorites  # type: ignore[assignment]

    response = client.get("/api/v1/favorites")
    assert response.status_code == 200
    body = response.json()
    assert len(body["favorites"]) == 2


def test_delete_favorite_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def delete_favorite(db, user_id: int, currency_symbol: str):
        assert user_id == 1
        assert currency_symbol == "BTC"
        return True

    favorites.favorites_service.delete_favorite = delete_favorite  # type: ignore[assignment]

    response = client.delete("/api/v1/favorites/BTC")
    assert response.status_code == 200
    assert response.json()["currency_symbol"] == "BTC"


def test_delete_favorite_not_found():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def delete_favorite(db, user_id: int, currency_symbol: str):
        return False

    favorites.favorites_service.delete_favorite = delete_favorite  # type: ignore[assignment]

    response = client.delete("/api/v1/favorites/ABC")
    assert response.status_code == 404
