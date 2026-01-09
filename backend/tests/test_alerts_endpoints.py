from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from cryptotracker.__main__ import get_app
from cryptotracker.api.endpoints import alerts
from cryptotracker.utils import auth


def _override_user():
    return SimpleNamespace(id=1, telegram_id=123)


def test_create_alert_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    created = SimpleNamespace(
        id=10,
        symbol="BTC",
        percent=1.5,
        direction="up",
        is_active=True,
        base_price=100.0,
        last_triggered_at=None,
        created_at=datetime(2024, 1, 1),
    )

    async def create_alert(db, user_id: int, payload):
        assert user_id == 1
        assert payload.symbol == "BTC"
        return created

    alerts.alerts_service.create_alert = create_alert  # type: ignore[assignment]

    response = client.post(
        "/api/v1/alerts",
        json={"symbol": "BTC", "percent": 1.5, "direction": "up"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["symbol"] == "BTC"
    assert body["direction"] == "up"


def test_create_alert_bad_request():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def create_alert(db, user_id: int, payload):
        raise ValueError("bad input")

    alerts.alerts_service.create_alert = create_alert  # type: ignore[assignment]

    response = client.post(
        "/api/v1/alerts",
        json={"symbol": "BTC", "percent": 1.5, "direction": "up"},
    )
    assert response.status_code == 400


def test_list_alerts_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    alerts_list = [
        SimpleNamespace(
            id=1,
            symbol="BTC",
            percent=1.5,
            direction="up",
            is_active=True,
            base_price=100.0,
            last_triggered_at=None,
            created_at=datetime(2024, 1, 1),
        ),
        SimpleNamespace(
            id=2,
            symbol="ETH",
            percent=2.0,
            direction="down",
            is_active=True,
            base_price=200.0,
            last_triggered_at=None,
            created_at=datetime(2024, 1, 2),
        ),
    ]

    async def list_alerts(db, user_id: int):
        assert user_id == 1
        return alerts_list

    alerts.alerts_service.list_alerts = list_alerts  # type: ignore[assignment]

    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    body = response.json()
    assert len(body["alerts"]) == 2


def test_delete_alert_success():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def delete_alert(db, user_id: int, alert_id: int):
        assert user_id == 1
        assert alert_id == 42
        return True

    alerts.alerts_service.delete_alert = delete_alert  # type: ignore[assignment]

    response = client.delete("/api/v1/alerts/42")
    assert response.status_code == 200
    body = response.json()
    assert body["alert_id"] == 42
    assert body["message"] == "Alert deleted successfully"


def test_delete_alert_not_found():
    app = get_app()
    app.dependency_overrides[auth.get_current_user] = _override_user
    client = TestClient(app)

    async def delete_alert(db, user_id: int, alert_id: int):
        return False

    alerts.alerts_service.delete_alert = delete_alert  # type: ignore[assignment]

    response = client.delete("/api/v1/alerts/999")
    assert response.status_code == 404
