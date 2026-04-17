# Cycling Weather Bot

## Purpose
A Telegram bot that sends a next-day cycling weather forecast at 8 PM PT. Supports per-user location management and on-demand weather commands.

## Tech Stack
- Python 3.14
- `python-telegram-bot[job-queue]` — bot framework + APScheduler-backed job queue
- `httpx` — async HTTP calls to Open-Meteo
- `python-dotenv` — loads `.env`
- `uv` for dependency management (`uv run src/main.py` to start)

## Key Files
- `SPEC.md` — specs for all commands and display formats. Read this before implementing any command.
- `data/bot_data` — per-user location storage via PicklePersistence (created at runtime).
- `.env` — `TOKEN` (Telegram bot token).

## Architecture
- `src/main.py` — entry point; registers all handlers and starts polling
- `src/forecast/` — API calls (Open-Meteo weather + AQI + geocoding) and data models
- `src/weather_handlers.py` — `/now`, `/today`, `/forecast`, `/week` commands
- `src/cycle_handlers.py` — `/cycle` command with per-hour riding verdict
- `src/location_handlers.py` — `/add`, `/remove`, `/locations` with ConversationHandler
- `src/bot_handlers.py` — `/start`
- `src/formatters.py` — output formatting for weather commands
- `src/labels.py` — WMO codes, Beaufort, UV, AQI label lookups
- Per-user locations stored in `data/bot_data` — resolved to lat/lon at add time, no repeated geocoding
- Weather data: Open-Meteo Forecast API + Air Quality API (no API key needed)

## Running
```
uv run src/main.py
```

## Conventions
- No type annotations unless asked
- No docstrings unless asked
- Keep functions small and focused
- Scheduled 8 PM send uses compact forecast format with [Show extended ▼] button
