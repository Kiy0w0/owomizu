# Termux (Android) Setup

<div align="center">

![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)
[![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/bkvMhwjSPG)

</div>

---

## Important Notes

- **Playwright/Chromium does not work on Termux.** The browser-based captcha solver won't function on Android. Captchas will need to be solved manually.
- Always install Termux from **[F-Droid](https://f-droid.org/en/packages/com.termux/)**, not the Play Store. The Play Store version is outdated and causes install failures.
- `curl-cffi` is not compatible with Termux. Don't install it.

---

## Step 1 — Set Up Termux

After installing from F-Droid, open Termux and run:

```bash
pkg update && pkg upgrade -y
termux-setup-storage
```

Grant the storage permission when Android asks. Then install what we need:

```bash
pkg install python git curl -y
pip install --upgrade pip setuptools wheel
```

---

## Step 2 — Clone and Install

```bash
cd ~
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu
```

Install dependencies **without** curl-cffi or playwright:

```bash
pip install discord.py-self aiohttp requests rich flask pytz aiosqlite Pillow
```

Don't run `pip install -r requirements.txt` directly — it'll try to install `playwright` and `curl-cffi` which will fail on Android.

---

## Step 3 — Set Up Your Token

Create `tokens.txt` in the bot folder:
```
YOUR_DISCORD_TOKEN CHANNEL_ID
```

**Getting your token on Android:**
1. Open Chrome and go to [discord.com](https://discord.com) — switch to desktop mode
2. Tap the three dots → More tools → Developer tools (or press F12 if using a keyboard)
3. Go to Console and paste:
```javascript
window.webpackChunkdiscord_app.push([[Math.random()],{},req=>{for(const m of Object.values(req.c).map(m=>m?.exports).filter(Boolean)){if(m.default?.getToken!==undefined)return copy(m.default.getToken());if(m.getToken!==undefined)return copy(m.getToken());}}]);
```
4. Copy the token that appears.

**Getting a Channel ID:**
- Discord app → Settings → Advanced → Developer Mode on
- Long-press the channel → Copy ID

---

## Step 4 — Run the Bot

```bash
cd ~/owomizu
python mizu.py
```

Dashboard will be at `http://localhost:1200` — open it in your browser.

---

## Keeping It Running

Android will kill background processes when the screen turns off. To prevent this:

**Acquire wake lock (keeps Termux alive):**
```bash
termux-wake-lock
```

**Run in background with logging:**
```bash
nohup python mizu.py > mizu.log 2>&1 &
```

Check if it's still running:
```bash
ps aux | grep mizu
```

**Disable battery optimization for Termux:**
Go to Android Settings → Apps → Termux → Battery → select "Unrestricted" or "Don't optimize".

---

## Auto-Start on Boot

Install **Termux:Boot** from F-Droid, then:

```bash
mkdir -p ~/.termux/boot
nano ~/.termux/boot/start-mizu.sh
```

Add:
```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/owomizu
termux-wake-lock
python mizu.py >> mizu.log 2>&1
```

Make it executable:
```bash
chmod +x ~/.termux/boot/start-mizu.sh
```

---

## Updating

```bash
cd ~/owomizu
git pull origin main
pip install discord.py-self aiohttp requests rich flask pytz aiosqlite Pillow --upgrade
python mizu.py
```

Don't run `python setup.py` for updates — it'll try to reinstall incompatible packages.

---

## Troubleshooting

**Ninja / build error when installing packages:**
```bash
pkg install clang cmake ninja -y
pip cache purge
pip install discord.py-self aiohttp requests rich flask pytz aiosqlite Pillow
```

**`curl-cffi` error:**
```bash
pip uninstall curl-cffi -y
pip install discord.py-self aiohttp requests
```

**Port 1200 already in use:**
```bash
pkill -f "python mizu.py"
python mizu.py
```
Or find and kill the process:
```bash
lsof -i :1200
kill -9 <PID>
```

**Bot stops after screen locks:**
Make sure you ran `termux-wake-lock` and disabled battery optimization for Termux.

**Storage permission issues:**
```bash
termux-setup-storage
```
Then go to Android Settings → Apps → Termux → Permissions → allow Storage.

**Package install fails:**
```bash
pkg clean && pkg update && pkg upgrade -y
```

---

## Tips

- Use a Bluetooth keyboard — typing long commands on a touchscreen is painful
- Split-screen Termux + Discord for easier monitoring
- Install **Termux:Widget** to add a home screen shortcut to start the bot

---

<div align="center">

[← Back to README](../README.md)

</div>
