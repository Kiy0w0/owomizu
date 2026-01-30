# 🍎 macOS Installation Guide

<div align="center">

![macOS](https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=macos&logoColor=F0F0F0)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

**Elegant automation for your Mac**

</div>

## 📋 **Prerequisites**

### System Requirements
- **macOS:** 10.14 (Mojave) or later
- **Architecture:** Intel x64 or Apple Silicon (M1/M2/M3)
- **Python:** 3.7 or higher
- **RAM:** Minimum 2GB
- **Storage:** 1GB free space
- **Network:** Stable internet connection

### Check Your System
```bash
# Check macOS version
sw_vers

# Check architecture
uname -m
# Output: x86_64 (Intel) or arm64 (Apple Silicon)

# Check Python version
python3 --version
# Should output: Python 3.7.x or higher
```

---

## 🚀 **Installation Methods**

### Method 1: Homebrew (Recommended)

#### Step 1: Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install Dependencies
```bash
# Install Python and Git
brew install python git

# Verify installation
python3 --version
git --version
```

#### Step 3: Clone Repository
```bash
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu
```

#### Step 4: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 5: Install Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# **IMPORTANT**: Install Browser Solver Requirements
pip install playwright aiosqlite aiohttp "discord.py-self"
playwright install chromium
```

#### Step 6: Run Setup
```bash
python3 setup.py
```

### Method 2: Native Python (Alternative)

#### Step 1: Install Xcode Command Line Tools
```bash
xcode-select --install
```

#### Step 2: Download Python (if needed)
Visit [python.org](https://www.python.org/downloads/macos/) and download Python 3.7+

#### Step 3: Follow steps 3-5 from Method 1

---

## ⚙️ **Apple Silicon (M1/M2/M3) Specific Setup**

### Rosetta 2 (if needed)
```bash
# Install Rosetta 2 for compatibility
sudo softwareupdate --install-rosetta
```

### Native ARM64 Dependencies
```bash
# Ensure you're using ARM64 Python
python3 -c "import platform; print(platform.machine())"
# Should output: arm64

# If using Homebrew on Apple Silicon
arch -arm64 brew install python git
```

---

## 🔧 **Configuration**

### Step 1: Token Setup
During setup, you'll be prompted to configure Discord tokens:

```
[0]how many accounts do you want run with Mizu Network? :
2

please enter your token for account #1 :
[Your Discord token here]

please enter channel id for account #1 :
[Channel ID where bot will operate]
```

### Step 2: Start the Bot
```bash
python3 mizu.py
```

### Step 3: Access Web Dashboard
```bash
# Dashboard will be available at:
open http://localhost:5000
```

---

## 🍎 **macOS-Specific Features**

### Launch Agent (Auto-Start)

Create a launch agent to start Mizu Network automatically:

#### Step 1: Create LaunchAgent Directory
```bash
mkdir -p ~/Library/LaunchAgents
```

#### Step 2: Create Plist File
```bash
nano ~/Library/LaunchAgents/com.mizunetwork.bot.plist
```

#### Step 3: Add Configuration
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mizunetwork.bot</string>
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
    <key>StandardOutPath</key>
    <string>/tmp/owomizu.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/owomizu.error.log</string>
</dict>
</plist>
```

#### Step 4: Load Launch Agent
```bash
launchctl load ~/Library/LaunchAgents/com.mizunetwork.bot.plist
launchctl start com.mizunetwork.bot
```

#### Step 5: Manage Service
```bash
# Check status
launchctl list | grep mizunetwork

# Stop service
launchctl stop com.mizunetwork.bot

# Unload service
launchctl unload ~/Library/LaunchAgents/com.mizunetwork.bot.plist
```

### Menu Bar Integration

Create a simple menu bar app using Automator:

#### Step 1: Open Automator
- Applications → Automator → New Document → Application

#### Step 2: Add Shell Script Action
```bash
#!/bin/bash
cd /path/to/owomizu
source venv/bin/activate
python3 mizu.py
```

#### Step 3: Save as Application
- Save to Applications folder as "Mizu Network"

### Notifications (Optional)

Install terminal-notifier for native notifications:
```bash
brew install terminal-notifier

# Test notification
terminal-notifier -title "Mizu Network" -message "Bot is running!" -sound default
```

---

## 🔧 **Advanced Configuration**

### Environment Variables
```bash
# Add to ~/.zshrc or ~/.bash_profile
export MIZU_HOME="/path/to/owomizu"
export PATH="$MIZU_HOME/venv/bin:$PATH"

# Reload shell
source ~/.zshrc  # or source ~/.bash_profile
```

### Aliases for Easy Management
```bash
# Add to ~/.zshrc or ~/.bash_profile
alias mizu-start="cd $MIZU_HOME && source venv/bin/activate && python3 mizu.py"
alias mizu-stop="pkill -f mizu.py"
alias mizu-logs="tail -f $MIZU_HOME/logs/mizu.log"
alias mizu-update="cd $MIZU_HOME && git pull && pip install -r requirements.txt"
```

### Security Settings

#### Gatekeeper (for downloaded executables)
```bash
# If you encounter "unidentified developer" errors
sudo spctl --master-disable  # Temporarily disable
# Run your app
sudo spctl --master-enable   # Re-enable
```

#### Firewall Configuration
- System Preferences → Security & Privacy → Firewall
- Add Python to allowed apps if prompted

---

## 🐛 **Troubleshooting**

### Common Issues

**1. Command not found: python3**
```bash
# Install Python via Homebrew
brew install python

# Or create symlink
ln -s /usr/bin/python3 /usr/local/bin/python3
```

**2. Permission denied errors**
```bash
# Fix permissions
chmod +x setup.py
chmod +x mizu.py

# Or run with explicit python
python3 setup.py
```

**3. SSL Certificate errors**
```bash
# Update certificates
/Applications/Python\ 3.x/Install\ Certificates.command

# Or install via Homebrew
brew install ca-certificates
```

**4. Port 5000 already in use (AirPlay Receiver)**
```bash
# Disable AirPlay Receiver
# System Preferences → Sharing → AirPlay Receiver → Off

# Or change port in config
```

**5. Virtual environment issues**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Apple Silicon Specific Issues

**1. Architecture mismatch**
```bash
# Check Python architecture
python3 -c "import platform; print(platform.machine())"

# Use Rosetta if needed
arch -x86_64 python3 setup.py
```

**2. Homebrew path issues**
```bash
# Add Homebrew to PATH for Apple Silicon
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## 📊 **Performance Optimization**

### Activity Monitor
- Monitor CPU and memory usage
- Applications → Utilities → Activity Monitor

### Resource Management
```bash
# Check system resources
top -l 1 | grep "CPU usage"
vm_stat | head -5

# Optimize Python performance
export PYTHONOPTIMIZE=1
```

### Background App Refresh
- System Preferences → General → Login Items
- Remove unnecessary startup items

---

## 🔄 **Updates**

### Homebrew Updates
```bash
# Update Homebrew
brew update && brew upgrade

# Update Python
brew upgrade python
```

### Mizu Network Updates
```bash
cd owomizu
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Update browser binaries if needed
pip install playwright --upgrade
playwright install chromium
```

### Automated Update Script
```bash
# Create update script
nano ~/update-mizu.sh
```

```bash
#!/bin/bash
echo "🔄 Updating Mizu Network..."
cd ~/owomizu
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
echo "✅ Update complete!"
osascript -e 'display notification "Mizu Network updated successfully!" with title "Update Complete"'
```

```bash
chmod +x ~/update-mizu.sh
```

---

## 📱 **Integration with macOS Apps**

### Shortcuts App
Create shortcuts for common tasks:
1. Open Shortcuts app
2. Create new shortcut
3. Add "Run Shell Script" action
4. Add your commands

### Alfred Workflows (if installed)
Create custom Alfred workflows for bot management.

### Touch Bar (MacBook Pro)
Customize Touch Bar to include Mizu Network controls.

---

## 📞 **Support**

### Log Files
```bash
# View logs
tail -f logs/mizu.log

# System logs
log show --predicate 'process == "python3"' --last 1h
```

### System Information
```bash
# Gather system info for support
system_profiler SPSoftwareDataType
system_profiler SPHardwareDataType
```

### Getting Help
1. **Check Console app for system logs**
2. **Join our Discord:** [Support Server](https://discord.gg/your-server)
3. **Create GitHub issue:** [Issues](https://github.com/kiy0w0/owomizu/issues)
4. **Apple Developer Forums for macOS-specific issues**

---

## 🎨 **Customization**

### Terminal Theme
```bash
# Install Oh My Zsh for better terminal
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Install Powerlevel10k theme
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

### iTerm2 Integration
- Download iTerm2 for better terminal experience
- Configure color schemes and fonts
- Set up profiles for Mizu Network

---

<div align="center">

**🍎 Happy Farming on macOS! 🌊**

*Elegant automation, Apple style*

[← Back to Main README](README.md)

</div>
