# Crypto Tracker Bot

Telegram bot for Crypto Tracker application.

## Setup

1. Create a bot via [BotFather](https://t.me/botfather)
2. Get your bot token
3. Create `.env` file in the `bot` directory:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` file and add your bot token:
   ```
   BOT_TOKEN=your_actual_bot_token_here
   API_BASE_URL=http://localhost:8080/api/v1
   ```

## Run

```bash
cd bot
uv sync
uv run python -m cryptotracker_bot
```

## Environment Variables

- `BOT_TOKEN` - Telegram bot token (required)
- `API_BASE_URL` - Backend API URL (default: http://localhost:8080/api/v1)

