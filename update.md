# 🌊 Mizu Network - Update Changelog

## 📅 Version 1.2.0 - Latest Updates

### 🆕 New Features

#### 💰 **Auto Sell Animals System**
- **Automatic sell when cash runs out** - Bot will automatically run `owo sell all` when cowoncy drops below threshold
- **Smart triggering** - Only triggers when balance < 50 cowoncy (configurable)
- **Rate limiting** - Maximum 3 triggers per hour to avoid spam detection
- **Cooldown system** - 5-10 minute cooldown after each auto-sell
- **Dashboard integration** - Real-time logging and notifications

#### 🎲 **RPP System (Run/Piku/Pup)**
- **Random command execution** - Automatically sends run/pup/piku commands every 1 minute
- **Natural behavior simulation** - Random selection from available commands
- **Smart execution** - Only runs when bot is active (not during captcha/sleep/huntbot)
- **Configurable system** - Easy enable/disable through dashboard
- **Anti-detection** - Natural timing patterns to avoid bot detection

#### 💎 **Auto Enhance System**
- **Auto Use Gems** - Automatically uses gems during hunting for better rewards
- **Auto Invest Essence** - Invests essence into huntbot efficiency and duration
- **Smart Management** - Configurable cooldowns and investment limits
- **Dashboard Control** - Full configuration through web interface
- **Performance Tracking** - Monitor gem usage and essence investments

#### 🚨 **Enhanced Safety System**
- **Improved Captcha Detection** - Multiple detection methods with auto-pause
- **Command Handler Optimization** - Better pause/resume logic for huntbot
- **Anti-Spam Protection** - Smart delays and rate limiting
- **Real-time Status** - Dashboard shows current bot state and activities
- **Error Recovery** - Automatic recovery from common errors

### 🔧 **Technical Improvements**

#### ⚙️ **Configuration Enhancements**
- Added `autoSell` configuration section
- Added `autoRandomCommands` (RPP) configuration section  
- Added `autoEnhance` configuration for gems and essence
- Enhanced command info with new priorities and colors
- Improved settings validation and error handling

#### 🎨 **Dashboard Improvements**
- New AutoEnhance settings panel with full configuration
- Enhanced status indicators with real-time updates
- Improved command logging with better filtering
- Better responsive design for all screen sizes
- Toast notifications for important events

#### 🛡️ **Security & Safety**
- Enhanced anti-detection with natural command patterns
- Improved rate limiting across all automation features
- Better error recovery and comprehensive logging
- Smart command scheduling to avoid detection patterns
- File reading safety with proper error handling

### 🐛 **Major Bug Fixes**
- **Fixed OWO Infinite Loop** - Bot no longer spams "owo" messages
- **Fixed Huntbot Conflicts** - Manual hunt/battle commands now work properly
- **Fixed Command Handler Stuck** - Bot properly pauses/resumes during huntbot
- **Fixed Integer Conversion Errors** - Better handling of superscript numbers
- **Fixed File Reading Issues** - Safe handling of missing tokens.txt
- **Fixed Dashboard Sync Issues** - Real-time updates now work correctly

---

## 📅 Version 1.1.0 - Previous Updates

### 🌐 **Web Dashboard Launch**
- Complete web-based dashboard interface
- Real-time statistics and monitoring
- Configuration management through web UI
- Beautiful dark theme with responsive design

### 🤖 **Core Bot Improvements**
- Enhanced command handling system
- Improved queue management
- Better error handling and recovery
- Multi-account support enhancements

---

## 📅 Version 1.0.0 - Initial Release

### 🚀 **Core Features**
- Auto farming for OwO Discord game
- Hunt, Battle, Daily, OwO command automation
- Mini games support (Slots, Coinflip)
- Captcha detection and handling
- Multi-platform support (Windows, Linux, macOS, Android)

### 🛡️ **Safety Features**
- Anti-detection measures
- Smart delay system
- Token encryption
- API monitoring

---

## 🔮 **Upcoming Features**

### 🎯 **Planned for Next Version**
- 🎪 **Advanced Gambling AI** - Smart betting strategies for slots and coinflip
- 📱 **Mobile App** - Companion app for monitoring and control
- 🎨 **Custom Themes** - Personalized dashboard themes and colors
- 🤖 **AI Chat Integration** - Smart responses to OwO bot messages
- 📊 **Advanced Analytics** - Detailed performance and earnings reports
- 🔄 **Enhanced Multi-Account** - Better rotation and management system

---

## 📝 **Installation Notes**

### 🔄 **How to Update**
1. Run `python updater.py` to check for updates
2. Follow the automatic update process
3. Restart the bot with `python mizu.py`
4. Check the dashboard at `http://localhost:5000`

### ⚠️ **Important Notes**
- Always backup your `tokens.txt` and `config/` folder before updating
- Some features may require reconfiguration after major updates
- Check Discord Terms of Service compliance when using automation

---

**Made with 💙 by Mizu Network Team**

*Stay Mizu Stay Water* 🌊
