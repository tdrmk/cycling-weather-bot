# Installation

Steps to run the bot as a systemd daemon on Linux.

## 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Install Python 3.14

Python 3.14 is not yet available in most distro package managers. Use pyenv:

```bash
curl https://pyenv.run | bash
pyenv install 3.14.0
```

Or check the [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) if on Ubuntu.

## 3. Create a system user

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin cyclebot
```

## 4. Clone the repo and build the virtual environment

```bash
git clone https://github.com/tdrmk/cycling-weather-bot /path/to/cycling-weather-bot
cd /path/to/cycling-weather-bot
uv sync
```

After any dependency changes, re-run `uv sync` and restart the service.

## 5. Create the data directory

```bash
mkdir -p /path/to/cycling-weather-bot/data
```

## 6. Set directory permissions

The repo is owned by you but readable by `cyclebot`. Only `data/` is writable by `cyclebot`.

```bash
sudo chown -R youruser:cyclebot /path/to/cycling-weather-bot
sudo chmod -R g+rX /path/to/cycling-weather-bot
sudo chown cyclebot:cyclebot /path/to/cycling-weather-bot/data
```

## 7. Set .env permissions

`TOKEN` must be readable by `cyclebot` but not by other users.

```bash
sudo chown youruser:cyclebot /path/to/cycling-weather-bot/.env
sudo chmod 640 /path/to/cycling-weather-bot/.env
```

## 8. Create the service file

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

## 9. Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable cycling-weather-bot
sudo systemctl start cycling-weather-bot
```

## 10. Verify

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
