# Crypto Tracker — Backend

## Описание

Backend-сервис проекта **Crypto Tracker** реализован на FastAPI и отвечает за:

- получение данных о криптовалютах (через CoinGecko API)
- хранение данных в PostgreSQL
- управление пользовательскими алертами
- расчёт условий срабатывания уведомлений
- предоставление REST API для frontend и Telegram-бота

---

## Архитектура и подход

Проект построен по модульной структуре:

- **API слой (endpoints)** — HTTP маршруты и обработчики запросов
- **Services** — бизнес-логика (получение цен, логика алертов и т.п.)
- **Models** — сущности БД (SQLAlchemy)
- **Schemas** — входные/выходные DTO-модели (Pydantic)
- **Config** — конфигурация приложения через переменные окружения

---

## Структура проекта

```text
backend/
 ├── cryptotracker/
 │   ├── api/
 │   │   ├── endpoints/
 │   │   ├── services/
 │   │   ├── models/
 │   │   └── schemas/
 │   ├── config/
 │   └── main.py
 ├── pyproject.toml
 └── Dockerfile