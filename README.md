<div align="center">

# 🌊 Mizu OwO 水

*Advanced Auto Farming Bot for OwO Discord Game*

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/bkvMhwjSPG)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Termux-brightgreen.svg)]()

![Mizu Network Banner](static/imgs/mizu.png)

**Fully automated, anti-ban, with Auto-Solve Captcha.**

</div>

---

##  Features

* **Auto Farming**: `hunt`, `battle`, `owo`, `pray` with randomized human-like delays.
* **Auto Captcha Solver**: image captcha with retry, plus web captcha detection on PC and Termux.
* **Rate Limit Handler**: auto pause when Discord or OwO throttles.
* **Sleep System**: schedule quiet hours so the bot does not run around the clock.
* **Antiban Detection**: watches for hidden unicode patterns from OwO and stops with a webhook alert.
* **Session Tracker**: local SQLite database records hunt, battle, command, and captcha stats per session.
* **Custom Commands**: define your own timed commands without editing code.
* **Giveaway Handling**: joins giveaways, deduplicates on restart, and scans back for missed ones.
* **Termux Support**: runs light on phone with an easy setup script.
* **Quest & Mini-Games**: daily quests, slots, coinflip.
* **Web Dashboard**: monitor stats, XP, and inventory in the browser.

---

##  Install

### Android (Termux)
```bash
pkg update && pkg upgrade -y
pkg install git -y
git clone https://github.com/kiy0w0/owomizu
cd owomizu
chmod +x setup_termux.sh
./setup_termux.sh
python mizu.py
```

### PC (Windows / Linux)
Requires Python 3.11 or 3.12 (Chrome needed for Web Solver on PC).
```bash
git clone https://github.com/kiy0w0/owomizu
cd owomizu
pip install -r requirements.txt
python setup.py
python mizu.py
```

OS-specific guides: [Windows](Tutor/windows.md), [Linux](Tutor/linux.md), [macOS](Tutor/macos.md), [Termux](Tutor/termux.md), [Docker VPS](Tutor/docker_vps.md).

---

##  Config

Config files live in `config/`:

* `settings.json`: per-account config (token, channel IDs, gamble, cooldowns).
* `global_settings.json`: system config (webhooks, captcha, dashboard).
* `danger.json`: risk gate for experimental features. All default `false`. Enable only when you understand the risk.
* `webhookContent.json`: webhook embed templates (titles, descriptions, colors). Edit text without touching code.

### danger.json gates
| Key | Enables | Risk |
|-----|---------|------|
| `allowAutoQuest` | Auto quest solving | Experimental. Quest actions can look unusual. |
| `allowLevelQuotes` | Quote fetching for level grind | External API quotes are a known selfbot signature. |
| `allowChannelSwitcher` | Hopping between channels | Can disrupt command flow and captcha handling. |

A gated feature stays off even if `enabled` is `true` in `settings.json` until its `danger.json` key is `true`.

---

##  Safety Tips

* Do not run 24/7. Use the `sleep` feature.
* Keep delays reasonable.
* Check logs when errors appear.

---

## 🤝 Contributing
Bug or feature? Open a PR. Join the Discord for help.

## ❤️ Supporters
<a href="https://github.com/diov825" style="text-decoration: none; display: inline-block; text-align: center;">
  <img src="https://github.com/diov825.png" width="50" height="50" style="border-radius: 50%;" alt="diov825"><br>
  <b>diov825</b>
</a>

**Disclaimer:** *This bot is for educational purposes only. Use at your own risk.* 🌊
