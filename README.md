<div align="center">

# <span style="color: #00FFFF;">🌊 Mizu OwO 水</span>

*Advanced Auto Farming Bot for OwO Discord Game*

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/yourinvite)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Termux-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

![Mizu Network Banner](static/imgs/mizu.png)

**The most chill yet OP OwO farming bot. Fully automated, anti-ban, and now supports Auto-Solve Captcha!**

</div>

---

## ✨ Key Features

*   **🌾 Auto Farming**: `hunt`, `battle`, `owo`, and `pray` run on their own. Uses randomized, human-like delays so you stay under the radar.
*   **🤖 Auto Captcha Solver**:
    *   **Image Captcha**: Automatically reads and solves text in images (powered by Aurabeam). Includes a smart retry system with multiple strategies.
    *   **Web Captcha**: Automatically detects "Verify" links.
        *   *PC*: Opens browser, checks login, and clicks verify for you.
        *   *Termux*: Automatically opens your phone's browser so you just have to tap.
*   **🛡️ Rate Limit Handler**: If Discord API is lagging or OwO says "slow down", the bot automatically takes a break. Safe and spam-free.
*   **📱 Termux Support**: optimized to run lightly on your phone. Comes with an easy setup script.
*   **📜 Quest & Mini-Games**: Can handle daily quests and play slots/coinflip if you want.
*   **📊 Web Dashboard**: Monitor bot stats, XP, and inventory via browser. Mobile-friendly too.

---

## 🚀 How to Install

### 📱 Android Users (Termux)
For the mobile farmers, here's the easy way:

1.  Open Termux (download from F-Droid, PlayStore version is outdated).
2.  Run these commands one by one:
    ```bash
    pkg update && pkg upgrade -y
    pkg install git -y
    git clone https://github.com/kiy0w0/owomizu
    cd owomizu
    ```
3.  Run the special Termux setup script (installs everything needed):
    ```bash
    chmod +x setup_termux.sh
    ./setup_termux.sh
    ```
4.  Once success, just run:
    ```bash
    python mizu.py
    ```

### 🖥️ PC Users (Windows/Linux)
1.  Make sure you have **Python 3.8** or higher installed.
2.  Clone this repo:
    ```bash
    git clone https://github.com/kiy0w0/owomizu
    cd owomizu
    ```
3.  Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If you want to use Web Solver on PC, you need Chrome installed)*
4.  Initial setup (enter tokens etc):
    ```bash
    python setup.py
    ```
5.  Start the bot:
    ```bash
    python mizu.py
    ```

## 📚 Detailed Guides
Need specific instructions for your OS?
*   [🪟 Windows Guide](Tutor/windows.md)
*   [🐧 Linux Guide](Tutor/linux.md)
*   [🍎 macOS Guide](Tutor/macos.md)
*   [📱 Termux Guide](Tutor/termux.md)
*   [🐳 Docker VPS Guide](Tutor/docker_vps.md)

---

## ⚙️ Config & Tips

Main config files are in the `config/` folder:
*   `settings.json`: User config (account token, channel IDs, gamble settings, etc).
*   `global_settings.json`: System config (webhooks, captcha features, etc).

**Safety Tips (Anti-Ban):**
*   Don't be greedy and run it 24/7 non-stop. Use the `sleep` feature in config.
*   Use reasonable delays, don't speedrun it.
*   Check logs occasionally if errors pop up.

---

## 🤝 Contributing
Found a bug or want to add a feature? Feel free to PR!
Join our Discord if you need help or just want to chat.

**Disclaimer:**
*This bot is for educational purposes only. Use at your own risk.* 🌊
