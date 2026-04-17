# Installation

Steps to run the bot as a systemd daemon on Linux.

## 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Create a system user

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin cyclebot
```

## 3. Clone the repo and build the virtual environment

```bash
sudo git clone https://github.com/tdrmk/cycling-weather-bot /opt/cycling-weather-bot
cd /opt/cycling-weather-bot
uv sync
```

After any dependency changes, re-run `uv sync` and restart the service.

## 4. Create the .env file

```bash
echo "TOKEN=your-telegram-bot-token" > /opt/cycling-weather-bot/.env
```

## 5. Set directory permissions

```bash
sudo chown -R cyclebot:cyclebot /opt/cycling-weather-bot
sudo chmod 600 /opt/cycling-weather-bot/.env
```

## 6. Create the service file

Create `/etc/systemd/system/cycling-weather-bot.service`:

```ini
[Unit]
Description=Cycling Weather Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=cyclebot
WorkingDirectory=/opt/cycling-weather-bot
EnvironmentFile=/opt/cycling-weather-bot/.env
ExecStart=/opt/cycling-weather-bot/.venv/bin/python src/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 7. Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable cycling-weather-bot
sudo systemctl start cycling-weather-bot
```

## 8. Verify

```bash
sudo systemctl status cycling-weather-bot
```

## Useful commands

```bash
# Tail live logs
journalctl -u cycling-weather-bot -f

# Restart after pulling new code
cd /opt/cycling-weather-bot
uv sync
sudo systemctl restart cycling-weather-bot

# Stop / start manually
sudo systemctl stop cycling-weather-bot
sudo systemctl start cycling-weather-bot
```
