# Linux Setup

<div align="center">

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
[![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/bkvMhwjSPG)

</div>

---

## Before You Start

You need **Python 3.11 or 3.12**. Most distros ship an older version, so check first:

```bash
python3 --version
```

If it's below 3.11, install it:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git -y
```

**Fedora:**
```bash
sudo dnf install python3.11 git -y
```

**Arch:**
```bash
sudo pacman -S python git
```

---

## Installation

```bash
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Using a virtual environment keeps things clean and avoids dependency conflicts with other Python projects on your system.

---

## Setting Up Your Token

Create `tokens.txt` in the bot folder. One account per line:

```
YOUR_DISCORD_TOKEN CHANNEL_ID
```

**Getting your token:**
1. Open Discord in your browser
2. Press `F12` → Console tab
3. Paste this:
```javascript
window.webpackChunkdiscord_app.push([[Math.random()],{},req=>{for(const m of Object.values(req.c).map(m=>m?.exports).filter(Boolean)){if(m.default?.getToken!==undefined)return copy(m.default.getToken());if(m.getToken!==undefined)return copy(m.getToken());}}]);
```
4. Token is now copied to clipboard.

**Getting a Channel ID:**
- Discord Settings → Advanced → enable **Developer Mode**
- Right-click the channel → **Copy ID**

---

## Running the Bot

```bash
source venv/bin/activate
python3 mizu.py
```

Dashboard will be at `http://localhost:1200` once it's running.

---

## Running in the Background

**Screen** is the easiest option:
```bash
sudo apt install screen -y
screen -S mizu
source venv/bin/activate
python3 mizu.py
# Detach: Ctrl+A then D
# Reattach later: screen -r mizu
```

**Or tmux if you prefer:**
```bash
tmux new -s mizu
source venv/bin/activate
python3 mizu.py
# Detach: Ctrl+B then D
# Reattach: tmux attach -t mizu
```

**systemd (if you want it to auto-start on boot):**

Create `/etc/systemd/system/owomizu.service`:
```ini
[Unit]
Description=OwOMizu Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/owomizu
ExecStart=/path/to/owomizu/venv/bin/python mizu.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable owomizu
sudo systemctl start owomizu
```

---

## Updating

```bash
cd owomizu
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
playwright install chromium
```

---

## Troubleshooting

**Permission denied on mizu.py:**
```bash
chmod +x mizu.py
```

**Module not found errors:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Port 1200 already in use:**
```bash
lsof -i :1200
kill -9 <PID>
```
Or just change the port in `config/global_settings.json` under `website.port`.

**Playwright / Chromium issues:**
```bash
pip install playwright --upgrade
playwright install chromium --with-deps
```

---

<div align="center">

[← Back to README](../README.md)

</div>
