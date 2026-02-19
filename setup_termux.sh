#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# OwOMizu - Termux Setup Script
# Copyright (c) 2026 MizuNetwork / Kiy0w0
# Part of the OwOMizu Project (https://github.com/Kiy0w0/owomizu)
# ============================================================
# 
# This script automatically installs all dependencies required
# to run OwOMizu on Termux (Android).
#
# Usage:
#   chmod +x setup_termux.sh
#   ./setup_termux.sh
#
# ============================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${PURPLE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║       🌊 OwOMizu - Termux Setup           ║${NC}"
echo -e "${PURPLE}║       Version 1.5.5                       ║${NC}"
echo -e "${PURPLE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# ---- Step 1: Update packages ----
echo -e "${CYAN}[1/7]${NC} Updating Termux packages..."
pkg update -y && pkg upgrade -y
echo -e "${GREEN}✔ Packages updated${NC}"
echo ""

# ---- Step 2: Install system dependencies ----
echo -e "${CYAN}[2/7]${NC} Installing system dependencies..."
pkg install -y python git libxml2 libxslt openssl
echo -e "${GREEN}✔ System dependencies installed${NC}"
echo ""

# ---- Step 3: Upgrade pip ----
echo -e "${CYAN}[3/7]${NC} Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✔ pip upgraded${NC}"
echo ""

# ---- Step 4: Install aiohttp (PINNED for compatibility) ----
echo -e "${CYAN}[4/7]${NC} Installing aiohttp (pinned to <3.10 for compatibility)..."
echo -e "${YELLOW}⚠ This is critical! aiohttp 3.10+ causes 'NoneType is not iterable' errors${NC}"
pip install "aiohttp<3.10"
echo -e "${GREEN}✔ aiohttp installed (compatible version)${NC}"
echo ""

# ---- Step 5: Install discord.py-self ----
echo -e "${CYAN}[5/7]${NC} Installing discord.py-self..."
pip install git+https://github.com/dolfies/discord.py-self@20ae80b398ec83fa272f0a96812140e14868c88f
echo -e "${GREEN}✔ discord.py-self installed${NC}"
echo ""

# ---- Step 6: Install remaining requirements ----
echo -e "${CYAN}[6/7]${NC} Installing remaining Python requirements..."
# Install each requirement individually to avoid failures stopping the entire process
while IFS= read -r requirement || [[ -n "$requirement" ]]; do
    # Skip comments, empty lines, and already-installed packages
    [[ -z "$requirement" ]] && continue
    [[ "$requirement" == \#* ]] && continue
    [[ "$requirement" == *"discord.py-self"* ]] && continue
    [[ "$requirement" == *"aiohttp"* ]] && continue
    # Skip desktop-only packages that don't work on Termux
    [[ "$requirement" == *"plyer"* ]] && continue
    [[ "$requirement" == *"playsound"* ]] && continue
    [[ "$requirement" == *"psutil"* ]] && continue
    [[ "$requirement" == *"pypresence"* ]] && continue
    # Skip heavy ML packages (optional for captcha solver)
    [[ "$requirement" == *"ddddocr"* ]] && continue
    [[ "$requirement" == *"opencv"* ]] && continue
    [[ "$requirement" == *"ultralytics"* ]] && continue
    [[ "$requirement" == *"selenium"* ]] && continue
    [[ "$requirement" == *"webdriver-manager"* ]] && continue
    
    echo -e "  Installing ${BLUE}${requirement}${NC}..."
    pip install "$requirement" 2>/dev/null || echo -e "  ${YELLOW}⚠ Failed to install ${requirement} (may be optional)${NC}"
done < requirements.txt
echo -e "${GREEN}✔ Requirements installed${NC}"
echo ""

# ---- Step 7: Install Termux-specific tools (optional) ----
echo -e "${CYAN}[7/7]${NC} Installing Termux notification tools (optional)..."
pkg install -y termux-api 2>/dev/null || echo -e "${YELLOW}⚠ termux-api not available (notifications won't work)${NC}"
echo -e "${GREEN}✔ Termux tools ready${NC}"
echo ""

# ---- Verify Installation ----
echo -e "${PURPLE}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}Verifying installation...${NC}"
echo ""

# Check Python
PYTHON_VER=$(python --version 2>&1)
echo -e "  Python:         ${GREEN}${PYTHON_VER}${NC}"

# Check aiohttp version
AIOHTTP_VER=$(python -c "import aiohttp; print(aiohttp.__version__)" 2>/dev/null || echo "NOT INSTALLED")
echo -e "  aiohttp:        ${GREEN}${AIOHTTP_VER}${NC}"

# Check if aiohttp is compatible
if python -c "
import aiohttp
v = tuple(int(x) for x in aiohttp.__version__.split('.')[:2])
exit(0 if v < (3, 10) else 1)
" 2>/dev/null; then
    echo -e "  aiohttp compat: ${GREEN}✔ Compatible${NC}"
else
    echo -e "  aiohttp compat: ${RED}✘ Version too high! Run: pip install aiohttp==3.9.5${NC}"
fi

# Check discord.py-self
DISCORD_VER=$(python -c "import discord; print(discord.__version__)" 2>/dev/null || echo "NOT INSTALLED")
echo -e "  discord.py:     ${GREEN}${DISCORD_VER}${NC}"

# Check flask
FLASK_VER=$(python -c "import flask; print(flask.__version__)" 2>/dev/null || echo "NOT INSTALLED")
echo -e "  Flask:          ${GREEN}${FLASK_VER}${NC}"

echo ""
echo -e "${PURPLE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 OwOMizu setup complete!${NC}"
echo ""
echo -e "To start the bot, run:"
echo -e "  ${CYAN}python mizu.py${NC}"
echo ""
echo -e "${YELLOW}⚠ Tips:${NC}"
echo -e "  1. Make sure your token is in ${BLUE}.env${NC} or ${BLUE}tokens.txt${NC}"
echo -e "  2. Configure settings in ${BLUE}config/settings.json${NC}"
echo -e "  3. Run ${CYAN}termux-wake-lock${NC} to prevent sleep during farming"
echo -e "  4. If you get 'NoneType' errors, run: ${CYAN}pip install aiohttp==3.9.5${NC}"
echo ""
