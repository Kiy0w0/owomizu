# Windows Setup

<div align="center">

![Windows](https://img.shields.io/badge/Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white)
[![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/bkvMhwjSPG)

</div>

---

## Before You Start

You'll need two things installed before anything else:

**Python 3.11 or 3.12** — Download it from [python.org](https://www.python.org/downloads/windows/).
When the installer opens, **check the box that says "Add Python to PATH"** before hitting install. A lot of people skip this and then wonder why nothing works.

**Git** — Grab it from [git-scm.com](https://git-scm.com/download/win). Default options during install are fine.

---

## Installation

Open a terminal (Command Prompt or PowerShell) and run:

```powershell
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu
pip install -r requirements.txt
playwright install chromium
```

That's it for the dependencies. If `pip` throws a permission error, add `--user` at the end of the pip command.

---

## Setting Up Your Token

Create a file called `tokens.txt` in the bot folder. Each line is one account, formatted as:

```
YOUR_DISCORD_TOKEN CHANNEL_ID
```

Example:
```
MTIxMTMyMjcwNDA4NzYxMzU1MQ.G8GlcG.example 1234567890123456789
```

**How to get your token:**
1. Open Discord in your browser at [discord.com](https://discord.com)
2. Press `F12` to open DevTools → go to the **Console** tab
3. Paste this and hit Enter:
```javascript
window.webpackChunkdiscord_app.push([[Math.random()],{},req=>{for(const m of Object.values(req.c).map(m=>m?.exports).filter(Boolean)){if(m.default?.getToken!==undefined)return copy(m.default.getToken());if(m.getToken!==undefined)return copy(m.getToken());}}]);
```
4. Your token is now in your clipboard.

**How to get a Channel ID:**
- Go to Discord Settings → Advanced → turn on **Developer Mode**
- Right-click the channel you want the bot to use → **Copy ID**

---

## Configuration

Before running, take a few minutes to look through `config/settings.json`. The important ones:

- `commands.hunt.enabled` / `commands.battle.enabled` — turn hunt and battle on/off
- `autoDaily` — auto claim daily rewards
- `autoUse.gems` — auto equip gems before hunting

`config/global_settings.json` handles dashboard settings, webhook notifications, and sleep behavior.

---

## Running the Bot

```powershell
python mizu.py
```

Once it starts, the web dashboard will be at `http://localhost:1200` — you can monitor and control everything from there.

**Running in the background:**

Create a `run.bat` file:
```batch
@echo off
title OwOMizu
python mizu.py
pause
```

Double-click it to start. The `pause` at the end keeps the window open if something crashes, so you can read the error.

---

## Updating

```powershell
git pull origin main
pip install -r requirements.txt --upgrade
playwright install chromium
```

---

## Troubleshooting

**"python is not recognized"**
Python isn't in your PATH. Reinstall Python and make sure to check the "Add to PATH" box.

**"No module named discord"**
```powershell
pip install -r requirements.txt
```

**"Improper Token" error**
Your token is invalid or expired. Re-extract it using the steps above — tokens reset when you change your password or log out.

**Dashboard not loading**
Check if port 1200 is already in use:
```powershell
netstat -an | findstr :1200
```
If it is, change the port in `config/global_settings.json` under `website.port`.

**Bot running slow / high CPU**
Increase the cooldown values in `settings.json` for hunt and battle. Values around 18–25 seconds are fine.

---

## Tips

- Add the bot folder to Windows Defender exclusions — it can slow down file access otherwise (Settings → Virus & threat protection → Exclusions)
- Use Windows Terminal instead of Command Prompt, it's a lot nicer to read
- Back up your `tokens.txt` and config files somewhere safe, just in case

---

<div align="center">

[← Back to README](../README.md)

</div>
