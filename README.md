<div align="center">

# <span style="color: #00FFFF;">🌊 Mizu OwO 水</span>

*Advanced Auto Farming Bot for OwO Discord Game*

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://mizu)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord Bot](https://img.shields.io/badge/Discord-Bot-7289da.svg)](https://discord.com/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/Version-1.5.5-cyan.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

![Mizu Network Banner](static/imgs/mizu.png)

**The most advanced, feature-rich, and user-friendly OwO farming bot**

</div>

---

## ✨ **Features**
*   **Smart Auto Farming:** Automates `hunt`, `battle`, `owo`, and `pray` with human-like delays.
*   **Quest Solver:** Automatically detects and solves daily quests (e.g. auto-enables slots for "Gamble 5 times").
*   **Mini-Games:** Strategies for Slots, Coinflip, and Lottery.
*   **Anti-Ban Technology:** Random sleep schedules, channel switching, and human-like typing simulation.
*   **Web Dashboard:** Real-time statistics and configuration from your browser (Mobile friendly).
*   **Auto-Upgrade:** Intelligently manages your HuntBot upgrades and essence investment.
*   **Multi-Account:** Run as many accounts as your PC can handle.

---

## 🚀 **Quick Start**
   ```bash
   python setup.py
   python mizu.py
   ```
   - Run `setup.py` first for an easy, interactive configuration.

2. **Access Dashboard:**
   Open: `http://localhost:1200` or `http://YOUR_LOCAL_IP:1200`

### ⚡ **One-Click Deploy**
No PC? No problem. Run Mizu OwO on the cloud for free (24/7).

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/new)
[![Run on Replit](https://repl.it/badge/github/kiy0w0/owomizu)](https://repl.it/github/kiy0w0/owomizu)

---

## 🛡️ **Is it Safe? (Transparency)**
We know you're worried about bans. Here is exactly how Mizu protects your account:

1.  **Human-like Typing:** The bot simulates typing status before sending messages.
2.  **Randomized Delays:** It never sends commands at perfect intervals (e.g., 15.2s, then 16.5s, then 14.8s).
3.  **Sleep Schedule:** You can set the bot to "sleep" for 8 hours a day, just like a real person.
4.  **Channel Switching:** The bot moves between channels so it doesn't look like a stationary turret.
5.  **Noise/Jitter:** Every action has a slight random time offset.

*Disclaimer: Automation always carries a small risk. We recommend using an alt account or the "Safe" profile in the setup wizard.*

### 🐳 **Docker Deployment**
> For a detailed VPS setup guide, check out the [**Docker VPS Tutorial**](/Tutor/docker_vps.md).
1. **Configure tokens:**
   Create `.env` in the project directory.

2. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   
3. **Access Dashboard:**
   Open: `http://localhost:1200`

### 🔄 **Auto-Update System**
```bash
# Update to latest version with settings preservation
python updater.py
```

---

## 📖 **Documentation**

### 📋 **Installation Guides**
- 🪟 [**Windows Setup**](/Tutor/windows.md) - Complete Windows installation guide
- 🐧 [**Linux Installation**](/Tutor/linux.md) - Ubuntu, Debian, CentOS setup
- 🍎 [**macOS Setup**](/Tutor/macos.md) - macOS installation guide  
- 📱 [**Termux (Android)**](/Tutor/termux.md) - Mobile setup guide
- 🐳 [**Docker VPS**](/Tutor/docker_vps.md) - 24/7 Hosting guide

### ⚙️ **Configuration**
- 🔑 **Token Setup** - Discord token extraction and setup
- ⚙️ **Settings** - `config/settings.json` configuration options
- 🌐 **Global Settings** - `config/global_settings.json` system settings
- 🎯 **Command Configuration** - Individual command customization

#### 🔒 Security & Tokens
We prioritize security. Instead of plain text files, we recommend using Environment Variables.

1.  Rename `.env.example` to `.env` (or create a new `.env` file).
2.  Add your tokens in the format:
    ```env
    TOKENS="YOUR_TOKEN_1 CHANNEL_ID_1;YOUR_TOKEN_2 CHANNEL_ID_2"
    ```
    *Note: Multiple accounts are separated by semicolons (;)*
3.  **Legacy Support:** `tokens.txt` is still supported but **deprecated**. Please migrate to `.env`.

### 🔧 **Advanced Features**
- 💎 **AutoEnhance** - Automatic gem usage and essence investment
- 🎯 **AutoHuntBot** - Huntbot automation and upgrades
- 💰 **AutoSell** - Smart item selling with triggers
- 🎲 **RPP System** - Random command execution
- 🔄 **Multi-Account** - Managing multiple Discord accounts

### 🛠️ **Development**
- 🤝 [**Contributing Guide**](/CONTRIBUTING.md) - How to contribute
- 📝 **API Documentation** - Internal API reference
- 🧪 **Testing** - Testing procedures and guidelines
- 🔧 **Development Setup** - Local development environment

---

## 🎨 **Screenshots**

<div align="center">

### 🖥️ Desktop CLI
![Desktop CLI](static/imgs/desktop_cli.jpg)

### 🌐 Web Dashboard
![Web Dashboard](static/imgs/web.png)

</div>

---

## 🔧 **API Integration**

### 🌐 **Mizu Network API**
Our bot integrates with the live Mizu API for enhanced functionality:

- 📡 **Status Monitoring** - Real-time service health checks
- 📢 **Announcements** - Important updates and news
- 🔄 **Version Checking** - Automatic update notifications
- 🛡️ **Safety Updates** - Security patches and warnings
- 📊 **Statistics** - Usage analytics and performance metrics

**API Endpoint:** `https://api.ive.my.id`

### 🎛️ **Web Dashboard API**
The bot includes a built-in REST API for the web dashboard:
- 📊 `/api/stats` - Real-time statistics
- ⚙️ `/api/settings` - Configuration management
- 🎮 `/api/commands` - Command control
- 📈 `/api/performance` - Performance metrics

---

## 🤝 **Contributing**

We welcome all types of contributions! Whether you're a developer, designer, or just want to help improve documentation.

### 🌟 **Ways to Contribute**
- 🐛 **Bug Reports** - Found an issue? Let us know!
- 💡 **Feature Requests** - Have ideas? Share them!
- 💻 **Code Contributions** - Fix bugs or add features
- 📖 **Documentation** - Help improve guides and docs
- 🎨 **Design** - UI/UX improvements
- 🌐 **Translations** - Help make Mizu multilingual

### 📋 **Getting Started**
1. Read our [**Contributing Guidelines**](/CONTRIBUTING.md)
2. Join our [**Discord Community**](https://4NsdaRWD2K)
3. Check [**Good First Issues**](https://github.com/kiy0w0/owomizu/labels/good%20first%20issue)

### 🔧 **Development Setup**
```bash
# Fork and clone the repository
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ **Disclaimer**

This bot is for educational purposes only. Use at your own risk. The developers are not responsible for any Discord account suspensions or bans that may result from using this bot.

---

## 🌟 **Support & Community**

<div align="center">

### 💬 **Get Help**
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/4NsdaRWD2K)
[![GitHub Issues](https://img.shields.io/badge/GitHub-Report%20Issues-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/kiy0w0/owomizu/issues)

### 🎯 **Quick Links**
| Need Help With | Go To |
|----------------|-------|
| 🐛 **Bug Reports** | [GitHub Issues](https://github.com/kiy0w0/owomizu/issues) |
| 💡 **Feature Requests** | [GitHub Discussions](https://github.com/kiy0w0/owomizu/discussions) |
| ❓ **General Questions** | [Discord #help](https://discord.gg/4NsdaRWD2K) |
| 💻 **Development** | [Discord #development](https://discord.gg/4NsdaRWD2K) |
| 📖 **Documentation** | [Wiki](https://github.com/kiy0w0/owomizu/wiki) |

**Made with 💙 by the Mizu Network Community**

*Stay Mizu, Stay Water* 🌊

</div>

---

<div align="center">

### 📊 **Stats**

![GitHub stars](https://img.shields.io/github/stars/kiy0w0/owomizu?style=social)
![GitHub forks](https://img.shields.io/github/forks/kiy0w0/owomizu?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/kiy0w0/owomizu?style=social)

![GitHub last commit](https://img.shields.io/github/last-commit/kiy0w0/owomizu)
![GitHub repo size](https://img.shields.io/github/repo-size/kiy0w0/owomizu)
![GitHub language count](https://img.shields.io/github/languages/count/kiy0w0/owomizu)

</div>

---
