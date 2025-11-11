## Диаграмма отношений моделей базы данных Crypto Tracker

### Текущие реализованные модели

```mermaid
erDiagram
    User ||--o{ Favorite : "has many"

    User {
        int id PK
        bigint telegram_id UK
        varchar username
        datetime created_at
        datetime updated_at
    }

    Favorite {
        int id PK
        int user_id FK
        varchar currency_symbol
        datetime created_at
    }
```

### Полная архитектура моделей (планируемые)

```mermaid
erDiagram
    User ||--o{ Favorite : "has many"
    User ||--o{ Portfolio : "has many"
    User ||--o{ Alert : "has many"
    User ||--|| UserSettings : "has one"

    Portfolio ||--o{ Lot : "has many"

    User {
        int id PK
        bigint telegram_id UK
        varchar username
        datetime created_at
        datetime updated_at
    }

    Favorite {
        int id PK
        int user_id FK
        varchar currency_symbol
        datetime created_at
    }

    Portfolio {
        int id PK
        int user_id FK
        varchar name
        decimal total_value
        datetime created_at
        datetime updated_at
    }

    Lot {
        int id PK
        int portfolio_id FK
        varchar currency_symbol
        decimal amount
        decimal purchase_price
        datetime purchase_date
    }

    Alert {
        int id PK
        int user_id FK
        varchar currency_symbol
        decimal threshold_percent
        varchar condition_type
        bool is_active
        datetime created_at
    }

    AlertTriggerLog {
        int id PK
        int alert_id FK
        decimal price_change_percent
        datetime triggered_at
    }

    UserSettings {
        int id PK
        int user_id FK
        varchar theme
        varchar notification_mode
        bool alerts_enabled
        datetime updated_at
    }
```

### Описание отношений

1. **User ↔ Favorite** (1:N)
   - Один пользователь может иметь множество избранных валют
   - Каскадное удаление: при удалении пользователя удаляются все его избранные валюты

2. **User ↔ Portfolio** (1:N) - планируется
   - Один пользователь может иметь множество портфелей
   - Портфель содержит виртуальные инвестиции пользователя

3. **Portfolio ↔ Lot** (1:N) - планируется
   - Один портфель может содержать множество лотов (инвестиций)
   - Лот представляет конкретную покупку определенной валюты

4. **User ↔ Alert** (1:N) - планируется
   - Один пользователь может создать множество алертов на уведомления
   - Алерты срабатывают при изменении цены валюты на заданный процент

5. **Alert ↔ AlertTriggerLog** (1:N) - планируется
   - Один алерт может иметь множество записей срабатываний
   - Лог хранит историю активации алертов

6. **User ↔ UserSettings** (1:1) - планируется
   - Один пользователь имеет одни настройки
   - Настройки включают тему интерфейса, режим уведомлений и т.д.

### Текущее состояние реализации

- ✅ **User** - полностью реализована
- ✅ **Favorite** - полностью реализована
- ❌ **Portfolio** - запланирована (фаза 2)
- ❌ **Lot** - запланирована (фаза 2)
- ❌ **Alert** - запланирована (фаза 3)
- ❌ **AlertTriggerLog** - запланирована (фаза 3)
- ❌ **UserSettings** - запланирована (фаза 3)

### Технологии

- **ORM**: SQLAlchemy 2.0 с асинхронной поддержкой
- **База данных**: PostgreSQL
- **Миграции**: Alembic (запланировано)
- **Кэширование**: aiocache для API ответов
