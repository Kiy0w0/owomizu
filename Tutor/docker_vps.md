# 🐳 Docker VPS Setup Guide

<div align="center">

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![VPS](https://img.shields.io/badge/VPS-Server-blueviolet?style=for-the-badge&logo=serverless&logoColor=white)

</div>

## 📋 **Prerequisites**

### System Requirements
- **OS:** Linux VPS (Ubuntu 20.04/22.04 LTS Recommended)
- **RAM:** Minimum 1GB (2GB Recommended)
- **Storage:** 5GB free space
- **Software:** Docker Engine & Docker Compose

---

## 🚀 **Installation Steps**

### Step 1: Install Docker & Docker Compose
First, update your system and install the necessary tools.

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install curl git -y
```

**Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**Verify Installation:**
```bash
docker --version
docker compose version
```

### Step 2: Clone Repository
Clone the Mizu OwO repository to your VPS:
```bash
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu
```

### Step 3: Configure Tokens
The Docker setup currently uses `tokens.txt` for account management.

1. **Create the file:**
   ```bash
   nano tokens.txt
   ```

2. **Add your accounts (One per line):**
   Format: `TOKEN CHANNEL_ID`
   
   ```text
   OTk5OTk5OTk5.G5.example 123456789012345678
   OTk5OTk5OTk5.G5.example2 876543210987654321
   ```

3. **Save and Exit:**
   Press `Ctrl+X`, then `Y`, then `Enter`.

### Step 4: Start the Bot
Run the bot in detached mode (background):
```bash
docker compose up -d
```
*Note: If `docker compose` doesn't work, try `docker-compose up -d`.*

The bot will now build the container and start running. This may take a few minutes the first time.

---

## 🌐 **Web Dashboard Access**

Once the bot is running, you can access the dashboard from your browser:

```
http://<YOUR_VPS_IP>:2000
```

**Firewall Settings:**
If you cannot access the dashboard, you may need to open port 2000:
```bash
sudo ufw allow 2000
```

---

## 🛠️ **Management Commands**

### View Logs
Check what the bot is doing:
```bash
docker compose logs -f
```
*(Press `Ctrl+C` to exit logs)*

### Stop the Bot
```bash
docker compose down
```

### Restart the Bot
```bash
docker compose restart
```

---

## 🔄 **Updating the Bot**

To update to the latest version of Mizu OwO using Docker:

```bash
# 1. Stop the bot
docker compose down

# 2. Pull latest code
git pull origin main

# 3. Rebuild the container (Important)
docker compose build --no-cache

# 4. Start again
docker compose up -d
```

---

## 🐛 **Troubleshooting**

### "Permission Denied"
If you get permission errors with Docker:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### "Tokens not found"
Ensure your `tokens.txt` is in the same folder as `docker-compose.yml`.

### Port Collision
If port 2000 is taken, edit `docker-compose.yml`:
```yaml
ports:
  - "3000:2000"  # Changes external port to 3000
```

---

<div align="center">

**🌊 Happy Farming!**

[← Back to Main README](../README.md)

</div>
