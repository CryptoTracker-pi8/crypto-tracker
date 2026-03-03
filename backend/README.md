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
```

### Где что находится

- `cryptotracker/main.py` — создание приложения FastAPI и подключение роутеров
- `cryptotracker/api/endpoints/` — HTTP endpoints
- `cryptotracker/api/services/` — сервисы с бизнес-логикой
- `cryptotracker/api/models/` — модели базы данных
- `cryptotracker/api/schemas/` — pydantic-схемы
- `cryptotracker/config/` — конфигурация приложения

---

## API Endpoints

### Health Check

GET `/health-check`

Проверка доступности backend-сервиса.

Пример ответа:

```json
{
  "status": "ok"
}
```

---

### Криптовалюты

GET `/api/v1/currencies`  
Возвращает список доступных криптовалют.

GET `/api/v1/currencies/{symbol}`  
Возвращает данные по конкретной валюте (например: btc, eth).

GET `/api/v1/currencies/{symbol}/history`  
Возвращает исторические данные по валюте.

---

### Алерты

POST `/api/v1/alerts`  
Создание пользовательского алерта.

Пример запроса:

```json
{
  "symbol": "btc",
  "target_price": 70000,
  "direction": "above"
}
```

GET `/api/v1/alerts`  
Получение списка активных алертов.

DELETE `/api/v1/alerts/{id}`  
Удаление алерта по ID.

---

## Запуск backend

### Локальный запуск

Перейти в папку backend:

```
cd backend
```

Установить зависимости:

```
pip install -e .
```

Запустить сервер:

```
uvicorn cryptotracker.main:app --reload
```

Backend будет доступен по адресу:

```
http://localhost:8000
```

---

## Документация API

Swagger UI доступен по адресу:

```
http://localhost:8000/swagger
```

OpenAPI схема:

```
http://localhost:8000/openapi
```