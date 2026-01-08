from types import SimpleNamespace

import pytest

from cryptotracker.api.services.favorite_service import FavoritesService
from cryptotracker.database.models import Favorite, User


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
    def __init__(self, existing_favorite=None, favorites=None, existing_user=None):
        self.existing_favorite = existing_favorite
        self.favorites = favorites or []
        self.existing_user = existing_user
        self.added = []
        self.deleted = []
        self.committed = False
        self.refreshed = []

    async def execute(self, query):
        if self.existing_user is not None:
            return _Result(item=self.existing_user)
        if self.existing_favorite is not None:
            return _Result(item=self.existing_favorite)
        return _Result(items=self.favorites)

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed.append(obj)

    async def delete(self, obj):
        self.deleted.append(obj)


@pytest.mark.asyncio
async def test_create_favorite_creates_new():
    db = _DB()
    service = FavoritesService()

    favorite = await service.create_favorite(db, user_id=1, currency_symbol="btc")
    assert isinstance(favorite, Favorite)
    assert favorite.currency_symbol == "BTC"
    assert db.added
    assert db.committed


@pytest.mark.asyncio
async def test_create_favorite_duplicate_raises():
    existing = Favorite(user_id=1, currency_symbol="BTC")
    db = _DB(existing_favorite=existing)
    service = FavoritesService()

    with pytest.raises(ValueError):
        await service.create_favorite(db, user_id=1, currency_symbol="BTC")


@pytest.mark.asyncio
async def test_get_user_favorites_returns_list():
    favorites = [
        Favorite(user_id=1, currency_symbol="BTC"),
        Favorite(user_id=1, currency_symbol="ETH"),
    ]
    db = _DB(favorites=favorites)
    service = FavoritesService()

    result = await service.get_user_favorites(db, user_id=1)
    assert result == favorites


@pytest.mark.asyncio
async def test_delete_favorite_missing_returns_false():
    db = _DB()
    service = FavoritesService()

    result = await service.delete_favorite(db, user_id=1, currency_symbol="BTC")
    assert result is False


@pytest.mark.asyncio
async def test_delete_favorite_deletes():
    existing = Favorite(user_id=1, currency_symbol="BTC")
    db = _DB(existing_favorite=existing)
    service = FavoritesService()

    result = await service.delete_favorite(db, user_id=1, currency_symbol="BTC")
    assert result is True
    assert db.deleted
    assert db.committed


@pytest.mark.asyncio
async def test_get_or_create_user_creates():
    db = _DB(existing_user=None)
    service = FavoritesService()

    user = await service.get_or_create_user_by_telegram_id(db, telegram_id=123, username="me")
    assert isinstance(user, User)
    assert user.telegram_id == 123
    assert db.added
    assert db.committed


@pytest.mark.asyncio
async def test_get_or_create_user_updates_username():
    existing = User(telegram_id=123, username="old")
    db = _DB(existing_user=existing)
    service = FavoritesService()

    user = await service.get_or_create_user_by_telegram_id(db, telegram_id=123, username="new")
    assert user.username == "new"
    assert db.committed
