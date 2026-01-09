from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from cryptotracker.__main__ import get_app
from cryptotracker.api.endpoints import portfolio
from cryptotracker.api.schemas.portfolio_schemas import PortfolioStats
from cryptotracker.utils import auth


def _override_user():
    return SimpleNamespace(id=1, telegram_id=123)


def test_create_portfolio_created():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    created = SimpleNamespace(id=1, user_id=1, name="My Portfolio", investments=[])

    async def upsert_portfolio(db, user_id: int, name: str, create: bool, new_name=None):
        assert user_id == 1
        assert create is True
        assert name == "My Portfolio"
        return created, True

    portfolio.svc.upsert_portfolio = upsert_portfolio  # type: ignore[assignment]

    response = client.post("/api/v1/portfolio", json={"name": "My Portfolio", "flag": True})
    assert response.status_code == 200
    assert response.json()["status"] == "created"


def test_create_portfolio_edited():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    edited = SimpleNamespace(id=1, user_id=1, name="New Name", investments=[])

    async def upsert_portfolio(db, user_id: int, name: str, create: bool, new_name=None):
        assert create is False
        assert new_name == "New Name"
        return edited, False

    portfolio.svc.upsert_portfolio = upsert_portfolio  # type: ignore[assignment]

    response = client.post(
        "/api/v1/portfolio",
        json={"name": "My Portfolio", "flag": False, "new_name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "edited"


def test_get_portfolio_not_found():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def get_portfolio(db, user_id: int):
        return None

    portfolio.svc.get_portfolio = get_portfolio  # type: ignore[assignment]

    response = client.get("/api/v1/portfolio")
    assert response.status_code == 404


def test_get_portfolio_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    portfolio_obj = SimpleNamespace(
        id=1,
        user_id=1,
        name="My Portfolio",
        investments=[
            SimpleNamespace(
                id=1,
                symbol="BTC",
                amount=1.0,
                buy_price=100.0,
                bought_at=datetime(2024, 1, 1),
            )
        ],
    )

    async def get_portfolio(db, user_id: int):
        return portfolio_obj

    portfolio.svc.get_portfolio = get_portfolio  # type: ignore[assignment]

    response = client.get("/api/v1/portfolio")
    assert response.status_code == 200
    assert response.json()["name"] == "My Portfolio"


def test_add_investment_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    investment = SimpleNamespace(
        id=1,
        symbol="BTC",
        amount=1.0,
        buy_price=100.0,
        bought_at=datetime(2024, 1, 1),
    )

    async def add_investment(db, user_id: int, symbol: str, amount: float, buy_price: float, bought_at=None):
        assert user_id == 1
        assert symbol == "BTC"
        return investment

    portfolio.svc.add_investment = add_investment  # type: ignore[assignment]

    response = client.post(
        "/api/v1/portfolio/investments",
        json={"symbol": "BTC", "amount": 1.0, "buy_price": 100.0},
    )
    assert response.status_code == 201
    assert response.json()["symbol"] == "BTC"


def test_add_investment_bad_request():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def add_investment(db, user_id: int, **kwargs):
        raise ValueError("bad input")

    portfolio.svc.add_investment = add_investment  # type: ignore[assignment]

    response = client.post(
        "/api/v1/portfolio/investments",
        json={"symbol": "BTC", "amount": 1.0, "buy_price": 100.0},
    )
    assert response.status_code == 400


def test_get_stats_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def get_stats(db, user_id: int):
        return PortfolioStats(
            total_invested=100.0,
            current_value=120.0,
            pnl_abs=20.0,
            pnl_pct=20.0,
        )

    portfolio.svc.get_stats = get_stats  # type: ignore[assignment]

    response = client.get("/api/v1/portfolio/stats")
    assert response.status_code == 200
    assert response.json()["current_value"] == "120.0"


def test_delete_investment_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def delete_investment(db, user_id: int, inv_id: int):
        assert user_id == 1
        assert inv_id == 5
        return True

    portfolio.svc.delete_investment = delete_investment  # type: ignore[assignment]

    response = client.delete("/api/v1/portfolio/investments/5")
    assert response.status_code == 200
    assert response.json()["message"] == "investment deleted successfully"


def test_delete_investment_not_found():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def delete_investment(db, user_id: int, inv_id: int):
        return False

    portfolio.svc.delete_investment = delete_investment  # type: ignore[assignment]

    response = client.delete("/api/v1/portfolio/investments/999")
    assert response.status_code == 404
