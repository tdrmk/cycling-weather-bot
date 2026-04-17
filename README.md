# Cycling Weather Bot

A Telegram bot that gives you cycling-specific weather forecasts. Check current conditions, get an hourly breakdown with a per-hour riding verdict, or see a 7-day summary — all for your saved locations.

## Commands

| Command | Description |
|---|---|
| `/now [city]` | Current conditions |
| `/today [city]` | Hourly forecast for today (compact table + extended toggle) |
| `/forecast [city] [day]` | Hourly forecast for any day up to 16 days ahead |
| `/week [city]` | 7-day daily summary |
| `/cycle [city] [day] [morning\|noon\|evening\|night]` | Cycling breakdown — per-hour verdict (Good / Manageable / Tough / Don't ride) with wind, rain, UV, AQI, and visibility |
| `/add [city]` | Add a location |
| `/remove` | Remove a saved location |
| `/locations` | List your saved locations |

All args are optional and can be given in any order. City defaults to your first saved location.

## Quick start

**Prerequisites:** Python 3.14+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Create a `.env` file in the repo root:
   ```
   TOKEN=your_telegram_bot_token
   ```
   To get a token, message [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot`, and follow the prompts.

3. Run:
   ```bash
   uv run src/main.py
   ```

## Data sources

- [Open-Meteo Forecast API](https://open-meteo.com) — hourly and daily weather
- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) — US AQI
- [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) — city search

No API key required.

## Stack

- Python 3.14
- [python-telegram-bot](https://python-telegram-bot.org) with job-queue
- [httpx](https://www.python-httpx.org) for async HTTP
- [uv](https://docs.astral.sh/uv/) for dependency management

## Production deployment

See [INSTALL.md](INSTALL.md) for running as a systemd service on Linux.
