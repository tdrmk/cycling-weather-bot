# Installation

Steps to run the bot as a systemd daemon on Linux.

## 1. Create a system user

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin cyclebot
```

## 2. Clone the repo

```bash
sudo git clone https://github.com/tdrmk/cycling-weather-bot /opt/cycling-weather-bot
```

## 3. Create the .env file

```bash
sudo sh -c 'echo "TOKEN=your-telegram-bot-token" > /opt/cycling-weather-bot/.env'
```

## 4. Set directory permissions

```bash
sudo chown -R cyclebot:cyclebot /opt/cycling-weather-bot
sudo chmod 600 /opt/cycling-weather-bot/.env
```

## 5. Install dependencies

```bash
sudo -u cyclebot python3 -m venv /opt/cycling-weather-bot/.venv
sudo -u cyclebot /opt/cycling-weather-bot/.venv/bin/pip install /opt/cycling-weather-bot
```

After any dependency changes, re-run the `pip install` line and restart the service.

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
ExecStart=/opt/cycling-weather-bot/.venv/bin/python -u src/main.py
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
sudo -u cyclebot git -C /opt/cycling-weather-bot pull
sudo -u cyclebot /opt/cycling-weather-bot/.venv/bin/pip install /opt/cycling-weather-bot
sudo systemctl restart cycling-weather-bot

# Stop / start manually
sudo systemctl stop cycling-weather-bot
sudo systemctl start cycling-weather-bot
```
