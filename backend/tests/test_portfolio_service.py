from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from cryptotracker.api.services.portfolio_service import PortfolioService
from cryptotracker.database.models import Investment, Portfolio, User


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
    def __init__(self, results=None):
        self.results = list(results or [])
        self.added = []
        self.deleted = []
        self.committed = False
        self.refreshed = []

    async def execute(self, query):
        if self.results:
            return self.results.pop(0)
        return _Result()

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed.append(obj)

    async def delete(self, obj):
        self.deleted.append(obj)


class _PriceService:
    def __init__(self, prices):
        self.prices = prices

    async def get_currency_by_symbol(self, symbol: str):
        value = self.prices.get(symbol)
        if isinstance(value, Exception):
            raise value
        return SimpleNamespace(price_usd=value)


@pytest.mark.asyncio
async def test_get_or_create_user_creates():
    db = _DB(results=[_Result(item=None)])
    service = PortfolioService()

    user = await service.get_or_create_user_by_telegram_id(db, telegram_id=123, username="me")
    assert isinstance(user, User)
    assert user.telegram_id == 123
    assert db.added
    assert db.committed


@pytest.mark.asyncio
async def test_get_or_create_user_updates_username():
    existing = User(telegram_id=123, username="old")
    db = _DB(results=[_Result(item=existing)])
    service = PortfolioService()

    user = await service.get_or_create_user_by_telegram_id(db, telegram_id=123, username="new")
    assert user.username == "new"
    assert db.committed
    assert db.refreshed


@pytest.mark.asyncio
async def test_upsert_portfolio_create_new():
    db = _DB()
    service = PortfolioService()

    async def _get_portfolio_by_user(db, user_id: int):
        return None

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]

    portfolio, created = await service.upsert_portfolio(
        db,
        user_id=1,
        name="My Portfolio",
        create=True,
    )
    assert created is True
    assert portfolio.name == "My Portfolio"
    assert db.added
    assert db.committed
    assert db.refreshed


@pytest.mark.asyncio
async def test_upsert_portfolio_create_duplicate_raises():
    db = _DB()
    service = PortfolioService()

    async def _get_portfolio_by_user(db, user_id: int):
        return Portfolio(user_id=user_id, name="Existing")

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]

    with pytest.raises(HTTPException) as excinfo:
        await service.upsert_portfolio(db, user_id=1, name="New", create=True)
    assert excinfo.value.status_code == 409


@pytest.mark.asyncio
async def test_upsert_portfolio_edit_missing_portfolio():
    db = _DB()
    service = PortfolioService()

    async def _get_portfolio_by_user(db, user_id: int):
        return None

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]

    with pytest.raises(HTTPException) as excinfo:
        await service.upsert_portfolio(db, user_id=1, name="My", create=False, new_name="New")
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_upsert_portfolio_edit_invalid_name():
    db = _DB()
    service = PortfolioService()
    portfolio = Portfolio(user_id=1, name="Old")

    async def _get_portfolio_by_user(db, user_id: int):
        return portfolio

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]

    with pytest.raises(HTTPException) as excinfo:
        await service.upsert_portfolio(db, user_id=1, name="Old", create=False, new_name=" ")
    assert excinfo.value.status_code == 422


@pytest.mark.asyncio
async def test_upsert_portfolio_edit_name_too_long():
    db = _DB()
    service = PortfolioService()
    portfolio = Portfolio(user_id=1, name="Old")

    async def _get_portfolio_by_user(db, user_id: int):
        return portfolio

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]

    with pytest.raises(HTTPException) as excinfo:
        await service.upsert_portfolio(
            db,
            user_id=1,
            name="Old",
            create=False,
            new_name="x" * 101,
        )
    assert excinfo.value.status_code == 422


@pytest.mark.asyncio
async def test_upsert_portfolio_edit_success():
    db = _DB()
    service = PortfolioService()
    portfolio = Portfolio(user_id=1, name="Old")

    async def _get_portfolio_by_user(db, user_id: int):
        return portfolio

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]

    updated, created = await service.upsert_portfolio(
        db,
        user_id=1,
        name="Old",
        create=False,
        new_name="Updated",
    )
    assert created is False
    assert updated.name == "Updated"
    assert db.committed
    assert db.refreshed


@pytest.mark.asyncio
async def test_add_investment_normalizes_datetime():
    db = _DB()
    service = PortfolioService()
    portfolio = Portfolio(id=1, user_id=1, name="My Portfolio")

    async def _get_portfolio_by_user(db, user_id: int):
        return portfolio

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]

    bought_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    inv = await service.add_investment(
        db,
        user_id=1,
        symbol="btc",
        amount=1.0,
        buy_price=100.0,
        bought_at=bought_at,
    )
    assert inv.symbol == "BTC"
    assert inv.bought_at.tzinfo is None
    assert inv.bought_at == datetime(2024, 1, 1)
    assert db.added
    assert db.committed


@pytest.mark.asyncio
async def test_add_investment_creates_portfolio_when_missing():
    db = _DB()
    service = PortfolioService()
    created_portfolio = Portfolio(id=2, user_id=1, name="My Portfolio")
    called = {"upsert": 0}

    async def _get_portfolio_by_user(db, user_id: int):
        return None

    async def upsert_portfolio(db, user_id: int, name: str, create: bool, new_name=None):
        called["upsert"] += 1
        return created_portfolio, True

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]
    service.upsert_portfolio = upsert_portfolio  # type: ignore[assignment]

    inv = await service.add_investment(
        db,
        user_id=1,
        symbol="eth",
        amount=2.0,
        buy_price=50.0,
    )
    assert called["upsert"] == 1
    assert inv.portfolio_id == 2


@pytest.mark.asyncio
async def test_delete_investment_missing_returns_false():
    db = _DB(results=[_Result(item=None)])
    service = PortfolioService()

    result = await service.delete_investment(db, user_id=1, inv_id=10)
    assert result is False


@pytest.mark.asyncio
async def test_delete_investment_deletes():
    existing = Investment(portfolio_id=1, symbol="BTC", amount=Decimal("1"), buy_price=Decimal("100"))
    db = _DB(results=[_Result(item=existing)])
    service = PortfolioService()

    result = await service.delete_investment(db, user_id=1, inv_id=10)
    assert result is True
    assert db.deleted
    assert db.committed


@pytest.mark.asyncio
async def test_get_stats_empty_portfolio():
    db = _DB()
    service = PortfolioService()

    async def _get_portfolio_by_user(db, user_id: int):
        return None

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]

    stats = await service.get_stats(db, user_id=1)
    assert stats.total_invested == 0
    assert stats.current_value == 0
    assert stats.pnl_abs == 0
    assert stats.pnl_pct == 0


@pytest.mark.asyncio
async def test_get_stats_calculates_values():
    investments = [
        Investment(portfolio_id=1, symbol="BTC", amount=Decimal("2"), buy_price=Decimal("100")),
        Investment(portfolio_id=1, symbol="ETH", amount=Decimal("1"), buy_price=Decimal("50")),
    ]
    db = _DB(results=[_Result(items=investments)])
    price_service = _PriceService({"BTC": 120.0, "ETH": 40.0})
    service = PortfolioService(prices=price_service)
    portfolio = Portfolio(id=1, user_id=1, name="My Portfolio")

    async def _get_portfolio_by_user(db, user_id: int):
        return portfolio

    service._get_portfolio_by_user = _get_portfolio_by_user  # type: ignore[assignment]

    stats = await service.get_stats(db, user_id=1)
    assert float(stats.total_invested) == 250.0
    assert float(stats.current_value) == 280.0
    assert float(stats.pnl_abs) == 30.0
    assert float(stats.pnl_pct) == 12.0
