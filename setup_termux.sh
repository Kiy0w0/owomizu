
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
echo -e "${PURPLE}║       Version 1.5.5                       ║${NC}"
echo -e "${PURPLE}╚═══════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}[1/7]${NC} Updating Termux packages..."
pkg update -y && pkg upgrade -y
echo -e "${GREEN}✔ Packages updated${NC}"
echo ""

echo -e "${CYAN}[2/7]${NC} Installing system dependencies..."
pkg install -y python git libxml2 libxslt openssl
echo -e "${GREEN}✔ System dependencies installed${NC}"
echo ""

echo -e "${CYAN}[3/7]${NC} Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✔ pip upgraded${NC}"
echo ""

echo -e "${CYAN}[4/7]${NC} Installing aiohttp (pinned to <3.10 for compatibility)..."
echo -e "${YELLOW}⚠ This is critical! aiohttp 3.10+ causes 'NoneType is not iterable' errors${NC}"
pip install "aiohttp<3.10"
echo -e "${GREEN}✔ aiohttp installed (compatible version)${NC}"
echo ""

echo -e "${CYAN}[5/7]${NC} Installing discord.py-self..."
pip install git+https://github.com/dolfies/discord.py-self@20ae80b398ec83fa272f0a96812140e14868c88f
echo -e "${GREEN}✔ discord.py-self installed${NC}"
echo ""

echo -e "${CYAN}[6/7]${NC} Installing remaining Python requirements..."
while IFS= read -r requirement || [[ -n "$requirement" ]]; do
    [[ -z "$requirement" ]] && continue
    [[ "$requirement" == \
    [[ "$requirement" == *"discord.py-self"* ]] && continue
    [[ "$requirement" == *"aiohttp"* ]] && continue
    [[ "$requirement" == *"plyer"* ]] && continue
    [[ "$requirement" == *"playsound"* ]] && continue
    [[ "$requirement" == *"psutil"* ]] && continue
    [[ "$requirement" == *"pypresence"* ]] && continue
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

echo -e "${CYAN}[7/7]${NC} Installing Termux notification tools (optional)..."
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

if python -c "
import aiohttp
v = tuple(int(x) for x in aiohttp.__version__.split('.')[:2])
exit(0 if v < (3, 10) else 1)
" 2>/dev/null; then
    echo -e "  aiohttp compat: ${GREEN}✔ Compatible${NC}"
else
    echo -e "  aiohttp compat: ${RED}✘ Version too high! Run: pip install aiohttp==3.9.5${NC}"
fi

DISCORD_VER=$(python -c "import discord; print(discord.__version__)" 2>/dev/null || echo "NOT INSTALLED")
echo -e "  discord.py:     ${GREEN}${DISCORD_VER}${NC}"

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
