# Docker / VPS Setup

<div align="center">

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
[![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/bkvMhwjSPG)

</div>

---

## Requirements

- A Linux VPS (Ubuntu 22.04 LTS works best)
- At least 1GB RAM, 5GB storage
- Docker installed

---

## Step 1 — Install Docker

```bash
sudo apt update && sudo apt install curl git -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Verify it worked:
```bash
docker --version
docker compose version
```

If you don't want to type `sudo` every time:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## Step 2 — Clone the Repository

```bash
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu
```

---

## Step 3 — Add Your Tokens

Create `tokens.txt` in the owomizu folder. One account per line:

```
YOUR_DISCORD_TOKEN CHANNEL_ID
```

Example:
```
MTIxMTMyMjcwNDA4NzYxMzU1MQ.G8GlcG.example 1234567890123456789
```

How to get your token and channel ID — see [windows.md](windows.md#setting-up-your-token) for the full steps (same process).

---

## Step 4 — Start the Bot

```bash
docker compose up -d
```

This builds the container and starts everything in the background. First run takes a few minutes while it downloads dependencies.

Check if it's running:
```bash
docker compose logs -f
```
Press `Ctrl+C` to stop watching logs — the bot keeps running.

---

## Dashboard Access

The dashboard runs on port `1200`. To access it from outside the VPS:

```bash
sudo ufw allow 1200
```

Then open `http://YOUR_VPS_IP:1200` in your browser.

If you use a cloud provider (AWS, DigitalOcean, etc.), make sure port 1200 is open in your firewall/security group settings too.

---

## Management

**Stop the bot:**
```bash
docker compose down
```

**Restart:**
```bash
docker compose restart
```

**View live logs:**
```bash
docker compose logs -f
```

---

## Updating

```bash
docker compose down
git pull origin main
docker compose build --no-cache
docker compose up -d
```

The `--no-cache` flag forces Docker to rebuild with the latest code. Without it, it might use a cached layer and miss changes.

---

## Troubleshooting

**"Permission denied" when running docker:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**"tokens.txt not found" error:**
Make sure `tokens.txt` is in the same directory as `docker-compose.yml`.

**Port 1200 already in use:**
Edit `docker-compose.yml` and change the external port:
```yaml
ports:
  - "1201:1200"  # access via port 1201 instead
```

**Container keeps restarting:**
```bash
docker compose logs --tail=50
```
Read the output — it'll tell you what's wrong. Usually it's a bad token or missing config.

**Out of disk space:**
```bash
docker system prune -a
```
This removes unused images and containers. Won't touch the running bot.

---

<div align="center">

[← Back to README](../README.md)

</div>
