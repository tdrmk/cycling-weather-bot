# Installation

Steps to run the bot as a systemd daemon on Linux.

## 1. Create a system user

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin cyclebot
```

## 2. Build the virtual environment

Run once as yourself from the repo root. After any dependency changes, re-run this and restart the service.

```bash
uv sync
```

## 3. Set directory permissions

The repo is owned by you but readable by `cyclebot`. Only `data/` is writable by `cyclebot`.

```bash
sudo chown -R youruser:cyclebot /path/to/cycling-weather-bot
sudo chmod -R g+rX /path/to/cycling-weather-bot
sudo chown cyclebot /path/to/cycling-weather-bot/data
```

## 4. Set .env permissions

`TOKEN` must be readable by `cyclebot` but not by other users.

```bash
sudo chown youruser:cyclebot /path/to/cycling-weather-bot/.env
sudo chmod 640 /path/to/cycling-weather-bot/.env
```

## 5. Create the service file

Create `/etc/systemd/system/cycling-weather-bot.service`:

```ini
[Unit]
Description=Cycling Weather Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=cyclebot
WorkingDirectory=/path/to/cycling-weather-bot
EnvironmentFile=/path/to/cycling-weather-bot/.env
ExecStart=/path/to/cycling-weather-bot/.venv/bin/python src/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 6. Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable cycling-weather-bot
sudo systemctl start cycling-weather-bot
```

## 7. Verify

```bash
sudo systemctl status cycling-weather-bot
```

## Useful commands

```bash
# Tail live logs
journalctl -u cycling-weather-bot -f

# Restart after pulling new code
uv sync
sudo systemctl restart cycling-weather-bot

# Stop / start manually
sudo systemctl stop cycling-weather-bot
sudo systemctl start cycling-weather-bot
```
