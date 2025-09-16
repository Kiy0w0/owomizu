# 🌊 Mizu Network - Update Changelog

## 📅 Version 1.2.0 - Latest Updates

### 🆕 New Features

#### 💰 **Auto Sell Animals System**
- **Automatic sell when cash runs out** - Bot will automatically run `owo sell all` when cowoncy drops below threshold
- **Smart triggering** - Only triggers when balance < 50 cowoncy (configurable)
- **Rate limiting** - Maximum 3 triggers per hour to avoid spam detection
- **Cooldown system** - 5-10 minute cooldown after each auto-sell
- **Dashboard integration** - Real-time logging and notifications

#### 🎲 **Automatic Run Piku PuP (RPP)**
- **Natural behavior simulation** - Automatically sends run/pup/piku commands
- **Smart scheduling** - Random intervals between 30-120 minutes
- **Rate limiting** - Maximum 8 commands per hour
- **Intelligent execution** - Only runs when bot is active (not during captcha/sleep)
- **Configurable commands** - Customizable command list and intervals

#### 🚨 **Enhanced Captcha Detection System**
- **Automatic stop** - Bot immediately stops all commands when captcha is detected
- **Automatic resume** - Bot automatically resumes after captcha is solved
- **Multiple detection methods** - Buttons, attachments, embeds, text-based detection
- **Real-time dashboard notifications** - Visual alerts with pulsing orange status dot
- **Enhanced logging** - Detailed captcha events in console and dashboard

#### 📊 **Improved Web Dashboard**
- **Real-time command logging** - Live activity feed with filtering options
- **Quick settings toggles** - Easy enable/disable for Hunt, Battle, Daily, OwO commands
- **Enhanced status monitoring** - Visual indicators for online/offline/captcha/paused states
- **Account statistics breakdown** - Per-account cowoncy, hunts, and battles tracking
- **Live notifications** - Toast notifications for important events

### 🔧 **Technical Improvements**

#### ⚙️ **Configuration Enhancements**
- Added `autoSell` configuration section
- Added `autoRandomCommands` configuration section  
- Enhanced command info with new priorities and colors
- Improved settings validation and error handling

#### 🎨 **UI/UX Improvements**
- New status indicators with animations
- Enhanced color coding for different command types
- Improved responsive design for dashboard
- Better error handling and user feedback

#### 🛡️ **Security & Safety**
- Enhanced anti-detection with random command patterns
- Improved rate limiting across all features
- Better error recovery and logging
- Smart command scheduling to avoid patterns

### 🐛 **Bug Fixes**
- Fixed dashboard status not updating correctly
- Fixed toggle buttons overlapping with text
- Improved error handling for missing configuration files
- Enhanced stability for long-running sessions

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
- Advanced gambling strategies
- Enhanced multi-account rotation
- Custom command scripting
- Performance analytics
- Mobile app companion

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
