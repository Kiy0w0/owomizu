# macOS Setup

<div align="center">

![macOS](https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white)
[![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/bkvMhwjSPG)

</div>

---

## Before You Start

You need **Python 3.11 or 3.12** and **Git**.

The easiest way is through [Homebrew](https://brew.sh). If you don't have it yet:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install the dependencies:
```bash
brew install python@3.12 git
```

**Apple Silicon (M1/M2/M3) note:** Homebrew installs to `/opt/homebrew/` instead of `/usr/local/`. If commands aren't found after install, add this to your `~/.zshrc`:
```bash
export PATH="/opt/homebrew/bin:$PATH"
```
Then run `source ~/.zshrc`.

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

---

## Setting Up Your Token

Create `tokens.txt` in the bot folder:
```
YOUR_DISCORD_TOKEN CHANNEL_ID
```

**Getting your token:**
1. Open Discord in Safari or Chrome at [discord.com](https://discord.com)
2. Press `Cmd+Option+J` to open the Console
3. Paste this and press Enter:
```javascript
window.webpackChunkdiscord_app.push([[Math.random()],{},req=>{for(const m of Object.values(req.c).map(m=>m?.exports).filter(Boolean)){if(m.default?.getToken!==undefined)return copy(m.default.getToken());if(m.getToken!==undefined)return copy(m.getToken());}}]);
```
4. Token is copied to clipboard.

**Getting a Channel ID:**
- Discord → Settings → Advanced → turn on **Developer Mode**
- Right-click any channel → **Copy ID**

---

## Running the Bot

```bash
source venv/bin/activate
python3 mizu.py
```

Dashboard runs at `http://localhost:1200`.

---

## Running in the Background

**Using Screen:**
```bash
screen -S mizu
source venv/bin/activate
python3 mizu.py
# Detach: Ctrl+A then D
# Reattach: screen -r mizu
```

**Auto-start on login (Launch Agent):**

Create `~/Library/LaunchAgents/mizu.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>mizu.bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/owomizu/venv/bin/python</string>
        <string>/path/to/owomizu/mizu.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/owomizu</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Replace `/path/to/owomizu` with the actual path (use `pwd` inside the folder to find it), then load it:
```bash
launchctl load ~/Library/LaunchAgents/mizu.plist
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

**"python3 not found" or old Python version:**
```bash
brew install python@3.12
# Then use python3.12 explicitly if needed
```

**SSL certificate errors:**
```bash
# Find your Python version folder and run:
open /Applications/Python\ 3.12/Install\ Certificates.command
```

**Port 5000 conflict (macOS uses it for AirPlay Receiver):**
Go to System Settings → General → AirDrop & Handoff → turn off **AirPlay Receiver**. Or just change the port in `config/global_settings.json`.

**Playwright / Chromium won't install:**
```bash
pip install playwright --upgrade
playwright install chromium --with-deps
```

**"Operation not permitted" on first run:**
macOS may ask for terminal permissions. Allow it in System Settings → Privacy & Security → Full Disk Access.

---

## Handy Aliases

Add these to your `~/.zshrc` to make things easier:
```bash
alias mizu="cd ~/owomizu && source venv/bin/activate && python3 mizu.py"
alias mizu-update="cd ~/owomizu && git pull && source venv/bin/activate && pip install -r requirements.txt --upgrade"
```

Then just type `mizu` to start the bot.

---

<div align="center">

[← Back to README](../README.md)

</div>
