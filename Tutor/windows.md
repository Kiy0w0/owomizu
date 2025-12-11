# 🪟 Mizu OwO - Windows Installation & Setup Guide

<div align="center">

![Mizu OwO](../static/imgs/mizu.png)

**Complete Windows Setup Guide for Mizu OwO Bot**

[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/Vc7CVSE7bd)
[![Windows](https://img.shields.io/badge/Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

</div>

---

## 📋 Table of Contents

- [🔧 Prerequisites](#-prerequisites)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🚀 Running the Bot](#-running-the-bot)
- [🎛️ Web Dashboard](#️-web-dashboard)
- [🔄 Updates](#-updates)
- [❌ Troubleshooting](#-troubleshooting)
- [💡 Tips & Tricks](#-tips--tricks)

---

## 🔧 Prerequisites

### Required Software

#### 1. **Python 3.8+**
```powershell
# Download from official website
https://www.python.org/downloads/windows/

# Or install via Microsoft Store
# Search "Python" in Microsoft Store
```

**⚠️ Important**: Make sure to check "Add Python to PATH" during installation!

#### 2. **Git for Windows**
```powershell
# Download from official website
https://git-scm.com/download/win

# Or install via Chocolatey (if you have it)
choco install git
```

#### 3. **Discord Account**
- Valid Discord account with Developer Mode enabled
- Access to Discord servers where you want to use the bot

---

## 📦 Installation

### Method 1: Git Clone (Recommended)

#### Step 1: Open Command Prompt or PowerShell
```powershell
# Press Win + R, type "cmd" or "powershell", press Enter
# Or search "Command Prompt" / "PowerShell" in Start Menu
```

#### Step 2: Navigate to desired directory
```powershell
# Example: Navigate to Documents
cd %USERPROFILE%\Documents

# Or create a new folder
mkdir MizuBot
cd MizuBot
```

#### Step 3: Clone the repository
```powershell
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu
```

#### Step 4: Install dependencies
```powershell
# Install required packages
pip install -r requirements.txt

# If you get permission errors, try:
pip install --user -r requirements.txt
```

### Method 2: Download ZIP

#### Step 1: Download
1. Go to https://github.com/kiy0w0/owomizu
2. Click **"Code"** → **"Download ZIP"**
3. Extract to your desired location

#### Step 2: Install dependencies
```powershell
# Open Command Prompt in the extracted folder
# Right-click in folder → "Open in Terminal" (Windows 11)
# Or Shift + Right-click → "Open PowerShell window here" (Windows 10)

pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Step 1: Get Discord Token

#### Method A: Browser Developer Tools
1. **Open Discord in browser** (discord.com)
2. **Login** to your account
3. **Press F12** to open Developer Tools
4. **Go to Console tab**
5. **Paste this code**:
   ```javascript
   window.webpackChunkdiscord_app.push([
     [Math.random()],
     {},
     req => {
       for (const m of Object.keys(req.c)
         .map(x => req.c[x].exports)
         .filter(x => x)) {
         if (m.default && m.default.getToken !== undefined) {
           return copy(m.default.getToken());
         }
         if (m.getToken !== undefined) {
           return copy(m.getToken());
         }
       }
     },
   ]);
   console.log('%cToken copied to clipboard!', 'font-size: 20px; color: #00ff00;');
   ```
6. **Your token is now copied** to clipboard!

#### Method B: Discord Desktop App
1. **Open Discord Desktop App**
2. **Press Ctrl + Shift + I** to open Developer Tools
3. **Follow the same steps** as Method A

### Step 2: Setup Configuration

#### Create tokens.txt
```powershell
# Create tokens.txt file in the bot directory
notepad tokens.txt
```

**Add your token and channel ID**:
```
YOUR_DISCORD_TOKEN CHANNEL_ID_WHERE_BOT_WILL_WORK
```

**Example**:
```
MTIxMTMyMjcwNDA4NzYxMzU1MQ.G8GlcG.example_token_here 1234567890123456789
```

#### Get Channel ID
1. **Enable Developer Mode** in Discord:
   - User Settings → Advanced → Developer Mode ✅
2. **Right-click on the channel** where you want the bot to work
3. **Click "Copy ID"**
4. **Paste it in tokens.txt** after your token

### Step 3: Configure Settings

#### Basic Settings (config/settings.json)
```json
{
  "commands": {
    "hunt": {"enabled": true},
    "battle": {"enabled": true},
    "owo": {"enabled": true}
  },
  "autoDaily": true,
  "autoUse": {
    "gems": {"enabled": true}
  }
}
```

#### Global Settings (config/global_settings.json)
```json
{
  "channelSwitcher": {
    "enabled": false
  },
  "webDashboard": {
    "enabled": true,
    "port": 8080
  }
}
```

---

## 🚀 Running the Bot

### Method 1: Command Line

#### Basic Run
```powershell
python mizu.py
```

#### Run with specific Python version
```powershell
# If you have multiple Python versions
python3 mizu.py
py -3 mizu.py
```

#### Run in background (PowerShell)
```powershell
Start-Process python -ArgumentList "mizu.py" -WindowStyle Hidden
```

### Method 2: Batch Script

#### Create run.bat
```batch
@echo off
title Mizu OwO Bot
echo Starting Mizu OwO Bot...
python mizu.py
pause
```

#### Double-click run.bat to start!

### Method 3: Task Scheduler (Auto-start)

#### Create Scheduled Task
1. **Open Task Scheduler** (search in Start Menu)
2. **Create Basic Task**
3. **Name**: "Mizu OwO Bot"
4. **Trigger**: "When I log on"
5. **Action**: "Start a program"
6. **Program**: `python`
7. **Arguments**: `mizu.py`
8. **Start in**: `C:\path\to\your\bot\folder`

---

## 🎛️ Web Dashboard

### Access Dashboard
```
http://yourIP:2000
```

### Features
- ✅ **Real-time Statistics**
- ✅ **Command Control**
- ✅ **Settings Management**
- ✅ **Live Logs**
- ✅ **Performance Monitoring**

### Custom Port
Edit `config/global_settings.json`:
```json
{
  "webDashboard": {
    "enabled": true,
    "port": 3000
  }
}
```

---

## 🔄 Updates

### Automatic Update
```powershell
python updater.py
```

### Manual Update
```powershell
git pull origin main
pip install -r requirements.txt --upgrade
```

### Check Version
```powershell
git log --oneline -1
```

### Safe Library Refresh (Fix Errors)
If you encounter "Improper Token" or "Unexpected Argument" errors, try reinstalling the library to a stable version:
```powershell
pip uninstall discord.py-self -y
pip install discord.py-self
```

---

## ❌ Troubleshooting

### Common Issues

#### 1. **"python is not recognized"**
**Solution**: Add Python to PATH
```powershell
# Check if Python is installed
python --version

# If not working, reinstall Python with "Add to PATH" checked
# Or manually add Python to PATH in Environment Variables
```

#### 2. **"No module named 'discord'"**
**Solution**: Install dependencies
```powershell
pip install discord.py-self
pip install -r requirements.txt
```

#### 3. **"Permission denied" errors**
**Solution**: Run as administrator or use --user flag
```powershell
# Run Command Prompt as Administrator
# Or use:
pip install --user -r requirements.txt
```

#### 4. **"Token is invalid"**
**Solution**: Get fresh token
- Follow token extraction steps again
- Make sure token is complete (no spaces/line breaks)
- Check if account is not banned/limited

#### 5. **Bot not responding in Discord**
**Solution**: Check configuration
- Verify channel ID is correct
- Make sure bot has permissions in that channel
- Check if Discord.py-self is latest version

#### 6. **Web dashboard not loading**
**Solution**: Check port and firewall
```powershell
# Check if port is in use
netstat -an | findstr :8080

# Try different port in global_settings.json
# Check Windows Firewall settings
```

### Performance Issues

#### High CPU Usage
```json
// Reduce command frequency in settings.json
{
  "commands": {
    "hunt": {"enabled": true, "cooldown": 20},
    "battle": {"enabled": true, "cooldown": 20}
  }
}
```

#### Memory Leaks
```powershell
# Restart bot periodically
# Use Task Scheduler to restart daily
```

### Debug Mode
```powershell
# Run with debug logging
python mizu.py --debug

# Or enable in settings
"debugMode": true
```

---

## 💡 Tips & Tricks

### Windows-Specific Tips

#### 1. **Use Windows Terminal**
- Better than Command Prompt
- Supports tabs and themes
- Install from Microsoft Store

#### 2. **Create Desktop Shortcut**
```batch
# Create shortcut with target:
C:\Windows\System32\cmd.exe /k "cd /d C:\path\to\bot && python mizu.py"
```

#### 3. **Monitor with Task Manager**
- Check CPU/Memory usage
- End process if needed
- Monitor network activity

#### 4. **Use PowerShell ISE for editing**
- Better than Notepad for JSON files
- Syntax highlighting
- Built into Windows

#### 5. **Backup Configurations**
```powershell
# Create backup script
xcopy config\*.json backup\ /Y
xcopy tokens.txt backup\ /Y
```

### Performance Optimization

#### 1. **Exclude from Windows Defender**
- Add bot folder to exclusions
- Prevents scanning delays
- Settings → Virus & threat protection → Exclusions

#### 2. **Set High Priority**
```powershell
# In Task Manager:
# Right-click python.exe → Set priority → High
```

#### 3. **Disable Windows Updates during farming**
- Prevents unexpected restarts
- Use "Active Hours" in Windows Update settings

### Security Tips

#### 1. **Keep Token Private**
- Never share tokens.txt
- Add to .gitignore if using git
- Use environment variables for production

#### 2. **Regular Updates**
```powershell
# Update bot weekly
python updater.py

# Update Python packages monthly
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

#### 3. **Monitor for Bans**
- Use reasonable delays
- Don't run 24/7 without breaks
- Monitor Discord ToS changes

---

## 🎯 Quick Start Checklist

- [ ] ✅ Python 3.8+ installed with PATH
- [ ] ✅ Git installed
- [ ] ✅ Repository cloned/downloaded
- [ ] ✅ Dependencies installed (`pip install -r requirements.txt`)
- [ ] ✅ Discord token extracted
- [ ] ✅ Channel ID obtained
- [ ] ✅ tokens.txt created with token and channel ID
- [ ] ✅ Settings configured (config/settings.json)
- [ ] ✅ Bot started (`python mizu.py`)
- [ ] ✅ Web dashboard accessible (yourIP:2000)
- [ ] ✅ Bot responding in Discord

---

## 🆘 Need Help?

### Community Support
- 💬 **Discord Server**: [Join Mizu Community](https://discord.gg/Vc7CVSE7bd)
- 📝 **GitHub Issues**: [Report Problems](https://github.com/kiy0w0/owomizu/issues)
- 📖 **Documentation**: [Full Docs](https://github.com/kiy0w0/owomizu)

### Windows-Specific Help
- 🪟 **Windows Community**: [Microsoft Community](https://answers.microsoft.com/)
- 🐍 **Python on Windows**: [Python Windows Guide](https://docs.python.org/3/using/windows.html)
- 💻 **PowerShell Help**: [PowerShell Documentation](https://docs.microsoft.com/powershell/)

---

<div align="center">

**🌊 Happy Farming with Mizu OwO on Windows! 🪟**

*Made with ❤️ by the Mizu Network Community*

</div>
