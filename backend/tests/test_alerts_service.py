from decimal import Decimal
from types import SimpleNamespace

import pytest

from cryptotracker.api.schemas.alerts_schemas import AlertCreate
from cryptotracker.api.services.alerts_service import AlertsService
from cryptotracker.database.models import Alert


class _Result:
    def __init__(self, item=None, items=None):
        self._item = item
        self._items = items or []

    def scalar_one_or_none(self):
        return self._item

    def scalars(self):
        return self

    def all(self):
        return list(self._items)


class _DB:
    def __init__(self, result=None):
        self._result = result or _Result()
        self.added = []
        self.deleted = []
        self.committed = False
        self.refreshed = []

    async def execute(self, query):
        return self._result

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed.append(obj)

    async def delete(self, obj):
        self.deleted.append(obj)


class _PriceService:
    def __init__(self, price_usd=None):
        self.price_usd = price_usd

    async def get_currency_by_symbol(self, symbol: str):
        if self.price_usd is None:
            return None
        return SimpleNamespace(price_usd=self.price_usd)


@pytest.mark.asyncio
async def test_create_alert_duplicate_raises():
    existing = Alert(user_id=1, symbol="BTC", percent=Decimal("1.5"), direction="up")
    db = _DB(result=_Result(item=existing))
    service = AlertsService(price_service=_PriceService(price_usd=100.0))

    payload = AlertCreate(symbol="btc", percent=Decimal("1.5"), direction="up")
    with pytest.raises(ValueError):
        await service.create_alert(db, user_id=1, payload=payload)


@pytest.mark.asyncio
async def test_create_alert_currency_missing_raises():
    db = _DB(result=_Result(item=None))
    service = AlertsService(price_service=_PriceService(price_usd=None))

    payload = AlertCreate(symbol="btc", percent=Decimal("1.5"), direction="up")
    with pytest.raises(ValueError):
        await service.create_alert(db, user_id=1, payload=payload)


@pytest.mark.asyncio
async def test_create_alert_success():
    db = _DB(result=_Result(item=None))
    service = AlertsService(price_service=_PriceService(price_usd=100.0))

    payload = AlertCreate(symbol="btc", percent=Decimal("1.5"), direction="both")
    alert = await service.create_alert(db, user_id=1, payload=payload)

    assert alert.symbol == "BTC"
    assert alert.base_price == Decimal("100.0")
    assert db.added
    assert db.committed
    assert db.refreshed


@pytest.mark.asyncio
async def test_list_alerts_returns_list():
    alerts_list = [Alert(user_id=1, symbol="BTC", percent=Decimal("1.5"), direction="up")]
    db = _DB(result=_Result(items=alerts_list))
    service = AlertsService(price_service=_PriceService(price_usd=100.0))

    result = await service.list_alerts(db, user_id=1)
    assert result == alerts_list


@pytest.mark.asyncio
async def test_delete_alert_missing_returns_false():
    db = _DB(result=_Result(item=None))
    service = AlertsService(price_service=_PriceService(price_usd=100.0))

    result = await service.delete_alert(db, user_id=1, alert_id=10)
    assert result is False


@pytest.mark.asyncio
async def test_delete_alert_deletes():
    existing = Alert(user_id=1, symbol="BTC", percent=Decimal("1.5"), direction="up")
    db = _DB(result=_Result(item=existing))
    service = AlertsService(price_service=_PriceService(price_usd=100.0))

    result = await service.delete_alert(db, user_id=1, alert_id=10)
    assert result is True
    assert db.deleted
    assert db.committed


def test_calculate_change_percent_handles_zero_base():
    result = AlertsService.calculate_change_percent(Decimal("0"), Decimal("100"))
    assert result == Decimal("0")


def test_should_trigger_variants():
    change = Decimal("5")
    threshold = Decimal("3")
    assert AlertsService.should_trigger("up", change, threshold) is True
    assert AlertsService.should_trigger("down", change, threshold) is False
    assert AlertsService.should_trigger("both", change, threshold) is True


def test_normalize_symbol_list_uppercases():
    alerts_list = [
        SimpleNamespace(symbol="btc"),
        SimpleNamespace(symbol="Eth"),
    ]
    result = AlertsService.normalize_symbol_list(alerts_list)
    assert result == {"BTC", "ETH"}
