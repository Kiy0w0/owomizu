# 🐧 Linux Installation Guide

<div align="center">

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Debian](https://img.shields.io/badge/Debian-D70A53?style=for-the-badge&logo=debian&logoColor=white)
![Fedora](https://img.shields.io/badge/Fedora-294172?style=for-the-badge&logo=fedora&logoColor=white)

</div>

## 📋 **Prerequisites**

### System Requirements
- **OS:** Any Linux distribution (Ubuntu, Debian, Fedora, Arch, etc.)
- **Python:** 3.7 or higher
- **RAM:** Minimum 1GB
- **Storage:** 500MB free space
- **Network:** Stable internet connection

### Check Python Version
```bash
python3 --version
# Should output: Python 3.7.x or higher
```

---

## 🚀 **Installation Steps**

### Step 1: Update System Packages

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Fedora:**
```bash
sudo dnf update -y
```

**Arch Linux:**
```bash
sudo pacman -Syu
```

### Step 2: Install Python and Dependencies

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-pip python3-venv git curl -y
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip python3-virtualenv git curl -y
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip git curl
```

### Step 3: Clone Repository
```bash
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu
```

### Step 4: Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Project & Browser Dependencies
```bash
# Core requirements
pip3 install -r requirements.txt

# **IMPORTANT**: Browser Solver Dependencies
pip3 install playwright aiosqlite aiohttp "discord.py-self"
playwright install chromium
```

### Step 6: Run Setup Script
```bash
python3 setup.py
```

The setup will automatically:
- ✅ Install all required Python packages
- ✅ Download necessary dependencies
- ✅ Check API connectivity
- ✅ Guide you through token configuration

### Step 6: Configure Tokens
During setup, you'll be prompted to:
1. Enter the number of Discord accounts
2. Provide Discord tokens for each account
3. Set channel IDs for each account

**Example:**
```
[0]how many accounts do you want run with Mizu Network? :
2

please enter your token for account #1 :
YOUR_DISCORD_TOKEN_HERE

please enter channel id for account #1 :
123456789012345678
```

### Step 7: Start the Bot
```bash
python3 mizu.py
```

---

## 🌐 **Web Dashboard Access**

Once the bot is running, access the web dashboard:

```bash
# Open in default browser
xdg-open http://localhost:5000

# Or manually navigate to:
http://localhost:5000
```

---

## 🔧 **Advanced Configuration**

### Auto-Start on Boot (systemd)

1. **Create service file:**
```bash
sudo nano /etc/systemd/system/owomizu.service
```

2. **Add service configuration:**
```ini
[Unit]
Description=Mizu Network Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/owomizu
ExecStart=/path/to/owomizu/venv/bin/python mizu.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable owomizu
sudo systemctl start owomizu
```

4. **Check status:**
```bash
sudo systemctl status owomizu
```

### Running in Background (Screen/Tmux)

**Using Screen:**
```bash
# Install screen
sudo apt install screen  # Ubuntu/Debian
sudo dnf install screen  # Fedora

# Start in screen session
screen -S owomizu
python3 mizu.py

# Detach: Ctrl+A, then D
# Reattach: screen -r owomizu
```

**Using Tmux:**
```bash
# Install tmux
sudo apt install tmux  # Ubuntu/Debian
sudo dnf install tmux  # Fedora

# Start in tmux session
tmux new-session -d -s owomizu 'python3 mizu.py'

# Attach to session
tmux attach-session -t owomizu
```

---

## 🐛 **Troubleshooting**

### Common Issues

**1. Permission Denied Error:**
```bash
chmod +x setup.py
chmod +x mizu.py
```

**2. Python Module Not Found:**
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

**3. Port 5000 Already in Use:**
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process (replace PID)
sudo kill -9 PID
```

**4. Git Not Found:**
```bash
# Ubuntu/Debian
sudo apt install git

# Fedora
sudo dnf install git

# Arch
sudo pacman -S git
```

### Log Files
```bash
# Check bot logs
tail -f logs/mizu.log

# Check system logs
journalctl -u owomizu -f
```

---

## 🔄 **Updates**

### Manual Update
```bash
cd owomizu
git pull origin main
source venv/bin/activate
pip3 install -r requirements.txt --upgrade
pip3 install playwright --upgrade
playwright install chromium
python3 setup.py
```

### Auto-Update Script
Create `update.sh`:
```bash
#!/bin/bash
cd /path/to/owomizu
git pull origin main
source venv/bin/activate
pip3 install -r requirements.txt
sudo systemctl restart owomizu
```

Make executable and run:
```bash
chmod +x update.sh
./update.sh
```

---

## 🛡️ **Security Notes**

1. **Never share your Discord tokens**
2. **Use virtual environment for isolation**
3. **Run with non-root user**
4. **Keep system updated**
5. **Monitor bot activity**

---

## 📞 **Support**

If you encounter issues:

1. **Check logs:** `tail -f logs/mizu.log`
2. **Verify Python version:** `python3 --version`
3. **Check dependencies:** `pip3 list`
4. **Join our Discord:** [Support Server](https://discord.gg/bkvMhwjSPG)
5. **Create GitHub issue:** [Issues](https://github.com/kiy0w0/owomizu/issues)

---

<div align="center">

**🌊 Happy Farming on Linux! 🐧**

[← Back to Main README](README.md)

</div>
