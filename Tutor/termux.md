# 📱 Termux (Android) Installation Guide

<div align="center">

![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)
![Termux](https://img.shields.io/badge/Termux-000000?style=for-the-badge&logo=terminal&logoColor=white)

**Run Mizu Network on your Android device!**

</div>

## 📋 **Prerequisites**

### Required Apps
1. **Termux** - Terminal emulator for Android
   - Download from [F-Droid](https://f-droid.org/en/packages/com.termux/) (Recommended)
   - **⚠️ Do NOT use Google Play Store version** (outdated)

2. **Termux:API** (Optional but recommended)
   - Download from [F-Droid](https://f-droid.org/en/packages/com.termux.api/)
   - Enables system notifications

### System Requirements
- **Android:** 7.0+ (API level 24+)
- **RAM:** Minimum 2GB
- **Storage:** 1GB free space
- **Network:** Stable internet connection

---

## 🚀 **Installation Steps**

### Step 1: Setup Termux

1. **Install Termux from F-Droid**
2. **Open Termux and update packages:**
```bash
pkg update && pkg upgrade -y
```

3. **Grant storage permission:**
```bash
termux-setup-storage
```

### Step 2: Install Dependencies

```bash
# Install essential packages
pkg install python git curl wget -y

# Install build tools & compilers (important for avoiding ninja errors!)
pkg install clang cmake ninja rust binutils -y

# Install development libraries
pkg install libffi openssl readline sqlite zlib libjpeg-turbo libpng -y

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel
```

### Step 3: Clone Repository
```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu
```

### Step 4: Install Python Dependencies

**For Termux, use this optimized installation:**

```bash
# Option 1: Standard installation (may have issues)
python setup.py

# Option 2: Termux-optimized installation (Recommended)
pip install discord.py-self aiohttp requests rich flask pytz Pillow beautifulsoup4 lxml
```

**⚠️ Common Issue Fix:**
If you get `ninja` or `curl-cffi` errors, use Option 2 above.

**What gets installed:**
- ✅ `discord.py-self` - Discord selfbot library
- ✅ `aiohttp` - Async HTTP requests
- ✅ `requests` - HTTP library
- ✅ `rich` - Beautiful terminal output
- ✅ `flask` - Web dashboard
- ✅ `pytz` - Timezone support
- ✅ `Pillow` - Image processing
- ✅ `beautifulsoup4` & `lxml` - HTML parsing

### Step 5: Configure Discord Tokens

During setup, you'll be prompted:

```
[0]how many accounts do you want run with Mizu Network? :
1

please enter your token for account #1 :
[Paste your Discord token here]

please enter channel id for account #1 :
[Enter channel ID where bot will work]
```

**📱 Getting Discord Token on Mobile:**
1. Open Discord in browser (desktop mode)
2. Console
3. Type: `window.webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]);m.find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()`
4. Copy the token (without quotes)

### Step 6: Start the Bot
```bash
python mizu.py
```

---

## 🌐 **Web Dashboard Access**

### Method 1: Local Access
```bash
# Bot will show: "Website Dashboard: http://localhost:5000"
# Open in Android browser: http://localhost:5000
```

### Method 2: Network Access (Advanced)
```bash
# Find your device IP
ifconfig

# Access from other devices: http://YOUR_DEVICE_IP:5000
```

---

## 🔧 **Termux-Specific Features**

### Background Execution

**Acquire Wake Lock:**
```bash
termux-wake-lock
```

**Run in Background:**
```bash
# Start in background
nohup python mizu.py > mizu.log 2>&1 &

# Check if running
ps aux | grep mizu.py
```

### Notifications
If Termux:API is installed:
```bash
# Test notification
termux-notification --title "Mizu Network" --content "Bot is running!"
```

### Auto-Start on Device Boot

1. **Install Termux:Boot from F-Droid**
2. **Create startup script:**
```bash
mkdir -p ~/.termux/boot
nano ~/.termux/boot/start-mizu
```

3. **Add startup commands:**
```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/owomizu
termux-wake-lock
python mizu.py
```

4. **Make executable:**
```bash
chmod +x ~/.termux/boot/start-mizu
```

---

## ⚙️ **Termux Configuration**

### Optimize Performance
```bash
# Increase swap (if device supports)
pkg install tsu
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Custom Termux Theme
```bash
# Create colors.properties
nano ~/.termux/colors.properties
```

Add Mizu theme:
```properties
# Mizu Network Theme
background: #1a1a2e
foreground: #00ffff
color0: #000000
color1: #ff5555
color2: #50fa7b
color3: #f1fa8c
color4: #bd93f9
color5: #ff79c6
color6: #8be9fd
color7: #f8f8f2
```

### Custom Font
```bash
# Download and apply font
curl -fLo ~/.termux/font.ttf https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/FiraCode/Regular/complete/Fira%20Code%20Regular%20Nerd%20Font%20Complete.ttf

# Restart Termux to apply
```

---

## 🐛 **Troubleshooting**

### Common Issues

**0. 🔴 Port Already in Use Error**

Error: `Address already in use - Port 1200 is in use by another program`

This happens when a previous bot instance is still running.

```bash
# Solution 1: Kill old bot processes
pkill -f "python mizu.py"

# Solution 2: Find and kill specific process
# Find process using port 1200
lsof -i :1200
# Kill the process ID shown
kill -9 <PID>

# Solution 3: Change port in config
# Edit config/global_settings.json and change port to 1201 or another unused port

# Then start bot again
python mizu.py
```

**0.1 🔴 Event Loop Error in Thread**

Error: `There is no current event loop in thread 'Thread-3 (run_bot)'`

**✅ This is now fixed in the latest update!**

If you still see this error:
```bash
# Pull latest updates
cd ~/owomizu
git pull origin main

# Restart bot
python mizu.py
```

The fix automatically creates event loops for threads in Termux environment.

**1. 🔴 Ninja Build Error (`spawn.h` not found)**

This is the most common error in Termux!

```bash
# Fix: Install build tools
pkg install clang cmake ninja rust binutils -y

# Then reinstall
pip cache purge
pip install discord.py-self aiohttp requests rich flask pytz
```

**2. 🔴 curl-cffi Error (`libcurl-impersonate.so.4` not found)**

`curl-cffi` is not compatible with Termux.

```bash
# Solution: Skip curl-cffi and use standard libraries
pip uninstall curl-cffi discord.py -y
pip install discord.py-self aiohttp requests

# Bot will work fine without curl-cffi!
```

**3. 🔴 Failed Building Wheel Error**

```bash
# Clear cache and reinstall
pip cache purge
rm -rf ~/.cache/pip

# Install minimal requirements
pip install discord.py-self aiohttp requests rich flask pytz Pillow

# Run bot
python mizu.py
```

**4. 🟡 Package Installation Fails:**
```bash
pkg clean
pkg update
pkg upgrade -y
```

**5. 🟡 Python Module Errors:**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

**6. 🟡 Storage Permission Issues:**
```bash
termux-setup-storage
# Then grant permission in Android settings
# Settings → Apps → Termux → Permissions → Storage
```

**7. 🟡 Network Connection Issues:**
```bash
# Check network
ping -c 3 google.com

# Reset DNS
echo "nameserver 8.8.8.8" > $PREFIX/etc/resolv.conf
echo "nameserver 1.1.1.1" >> $PREFIX/etc/resolv.conf
```

**8. 🟡 Bot Stops When Screen Locks:**
```bash
# Acquire wake lock
termux-wake-lock

# Use background execution with logging
nohup python mizu.py > mizu.log 2>&1 &

# Check if running
ps aux | grep python
```

**9. 🟡 Import Error after Installation:**
```bash
# Reinstall specific module
pip uninstall [module-name] -y
pip install [module-name] --no-cache-dir
```

**10. 🟡 Permission Denied Errors:**
```bash
# Fix permissions
chmod +x mizu.py
chmod -R 755 ~/owomizu
```

### Performance Issues

**1. Low Memory:**
```bash
# Check memory usage
free -h

# Kill unnecessary processes
pkill -f "process_name"

# Clear cache
sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || echo "Need root for cache clear"
```

**2. Slow Performance:**
```bash
# Reduce bot delay settings in config
# Close other apps running in background
# Enable developer options → "Don't keep activities"
# Restart Termux session
```

**3. Disk Space Issues:**
```bash
# Check disk usage
df -h

# Clean up
pkg clean
apt autoremove -y
pip cache purge
rm -rf ~/.cache/*
```

---

## 🔧 **Quick Fix Commands**

### One-Liner Fresh Install
```bash
pkg update && pkg upgrade -y && termux-setup-storage && pkg install python git clang cmake ninja -y && cd ~/storage/downloads && git clone https://github.com/kiy0w0/owomizu.git && cd owomizu && pip install --upgrade pip && pip install discord.py-self aiohttp requests rich flask pytz Pillow && python mizu.py
```

### One-Liner Fix for Errors
```bash
pkg install clang cmake ninja -y && pip cache purge && pip uninstall curl-cffi discord.py -y && pip install discord.py-self aiohttp requests rich flask pytz && cd ~/owomizu && python mizu.py
```

### Reset Everything
```bash
cd ~ && rm -rf owomizu && pkg clean && pip cache purge && pkg install python git clang cmake ninja -y && git clone https://github.com/kiy0w0/owomizu.git && cd owomizu && pip install discord.py-self aiohttp requests rich flask pytz && python mizu.py
```

---

## 📱 **Android-Specific Tips**

### Battery Optimization
1. **Disable battery optimization for Termux:**
   - Settings → Apps → Termux → Battery → Don't optimize

2. **Enable background activity:**
   - Settings → Apps → Termux → Battery → Allow background activity

3. **Disable adaptive battery:**
   - Settings → Battery → Adaptive Battery → Off

### Network Settings
- Use WiFi for stability
- Avoid mobile data limits
- Consider unlimited data plan

### Security
- Don't install from unknown sources
- Keep Termux updated
- Use strong device lock screen

---

## 🔄 **Updates**

### Update Termux Packages
```bash
pkg update && pkg upgrade -y
```

### Update Mizu Network
```bash
cd ~/owomizu
git pull origin main
python setup.py  # If new dependencies
```

### Auto-Update Script
```bash
# Create update script
nano ~/update-mizu.sh
```

```bash
#!/data/data/com.termux/files/usr/bin/bash
echo "🔄 Updating Mizu Network..."
cd ~/owomizu
git pull origin main
pip install -r requirements.txt --upgrade
echo "✅ Update complete!"
```

```bash
chmod +x ~/update-mizu.sh
./update-mizu.sh
```

---

## 📞 **Support**

### Logs and Debugging
```bash
# Check bot logs
tail -f mizu.log

# Check Termux logs
logcat | grep Termux
```

### Getting Help
1. **Check Termux Wiki:** [Termux Wiki](https://wiki.termux.com/)
2. **Join our Discord:** [Support Server](https://discord.gg/bkvMhwjSPG)
3. **Create GitHub issue:** [Issues](https://github.com/kiy0w0/owomizu/issues)
4. **Termux Community:** r/termux on Reddit

---

## 🌟 **Pro Tips**

1. **Use external keyboard for easier typing**
2. **Enable developer options for better performance**
3. **Use split screen with Discord app**
4. **Set up SSH for remote access**
5. **Create shortcuts with Termux:Widget**

---

<div align="center">

**📱 Happy Farming!**

*Mizu Network - Pocked Edition*

[← Back to Main README](README.md)

</div>
