#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${PURPLE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║       🌊 OwOMizu - Termux Setup           ║${NC}"
echo -e "${PURPLE}║       Version 1.8.0 >_<                   ║${NC}"
echo -e "${PURPLE}╚═══════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}[1/8]${NC} Updating Termux packages..."
pkg update -y && pkg upgrade -y
echo -e "${GREEN}✔ Packages updated${NC}"
echo ""

echo -e "${CYAN}[2/8]${NC} Installing system dependencies..."
pkg install -y python git libxml2 libxslt openssl libjpeg-turbo
echo -e "${GREEN}✔ System dependencies installed${NC}"
echo ""

echo -e "${CYAN}[3/8]${NC} Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✔ pip upgraded${NC}"
echo ""

echo -e "${CYAN}[4/8]${NC} Installing discord.py-self..."
pip install "discord.py-self==2.1.0"
echo -e "${GREEN}✔ discord.py-self installed${NC}"
echo ""

echo -e "${CYAN}[5/8]${NC} Installing aiohttp..."
pip install "aiohttp>=3.10"
echo -e "${GREEN}✔ aiohttp installed${NC}"
echo ""

echo -e "${CYAN}[6/8]${NC} Installing numpy & pillow (pre-built Termux builds)..."
pip install numpy pillow
echo -e "${GREEN}✔ numpy & pillow installed${NC}"
echo ""

echo -e "${CYAN}[7/8]${NC} Installing remaining Python requirements..."
while IFS= read -r requirement || [[ -n "$requirement" ]]; do
    [[ -z "$requirement" ]] && continue
    [[ "$requirement" == \#* ]] && continue
    [[ "$requirement" == *"discord.py-self"* ]] && continue
    [[ "$requirement" == *"aiohttp"* ]] && continue
    [[ "$requirement" == *"numpy"* ]] && continue
    [[ "$requirement" == *"pillow"* ]] && continue
    [[ "$requirement" == *"Pillow"* ]] && continue
    [[ "$requirement" == *"plyer"* ]] && continue
    [[ "$requirement" == *"playsound"* ]] && continue
    [[ "$requirement" == *"pypresence"* ]] && continue
    [[ "$requirement" == *"ddddocr"* ]] && continue
    [[ "$requirement" == *"opencv"* ]] && continue
    [[ "$requirement" == *"onnxruntime"* ]] && continue
    [[ "$requirement" == *"ultralytics"* ]] && continue
    [[ "$requirement" == *"selenium"* ]] && continue
    [[ "$requirement" == *"webdriver-manager"* ]] && continue

    echo -e "  Installing ${BLUE}${requirement}${NC}..."
    pip install "$requirement" 2>/dev/null || echo -e "  ${YELLOW}⚠ Failed to install ${requirement} (skipping)${NC}"
done < requirements.txt
echo -e "${GREEN}✔ Requirements installed${NC}"
echo ""

echo -e "${CYAN}[8/8]${NC} Installing Termux notification tools (optional)..."
pkg install -y termux-api 2>/dev/null || echo -e "${YELLOW}⚠ termux-api not available (notifications won't work)${NC}"
echo -e "${GREEN}✔ Termux tools ready${NC}"
echo ""

echo -e "${PURPLE}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}Verifying installation...${NC}"
echo ""

PYTHON_VER=$(python --version 2>&1)
echo -e "  Python:         ${GREEN}${PYTHON_VER}${NC}"

AIOHTTP_VER=$(python -c "import aiohttp; print(aiohttp.__version__)" 2>/dev/null || echo "NOT INSTALLED")
echo -e "  aiohttp:        ${GREEN}${AIOHTTP_VER}${NC}"

DISCORD_VER=$(python -c "import discord; print(discord.__version__)" 2>/dev/null || echo "NOT INSTALLED")
echo -e "  discord.py:     ${GREEN}${DISCORD_VER}${NC}"

FLASK_VER=$(python -c "import flask; print(flask.__version__)" 2>/dev/null || echo "NOT INSTALLED")
echo -e "  Flask:          ${GREEN}${FLASK_VER}${NC}"

NUMPY_VER=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "NOT INSTALLED")
echo -e "  numpy:          ${GREEN}${NUMPY_VER}${NC}"

RICH_VER=$(python -c "import rich; print(rich.__version__)" 2>/dev/null || echo "NOT INSTALLED")
echo -e "  rich:           ${GREEN}${RICH_VER}${NC}"

echo ""
echo -e "${PURPLE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 OwOMizu v1.8.0 setup complete!${NC}"
echo ""
echo -e "To start the bot, run:"
echo -e "  ${CYAN}python mizu.py${NC}"
echo ""
echo -e "${YELLOW}⚠ Tips:${NC}"
echo -e "  1. Make sure your token is in ${BLUE}.env${NC} or ${BLUE}tokens.txt${NC}"
echo -e "  2. Configure settings in ${BLUE}config/settings.json${NC}"
echo -e "  3. Run ${CYAN}termux-wake-lock${NC} to prevent Termux from sleeping"
echo -e "  4. If any package fails, try: ${CYAN}pkg install python-cryptography${NC}"
echo ""
