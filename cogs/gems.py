"""
Mizu OwO Bot
Copyright (C) 2025 MizuNetwork
Copyright (C) 2025 Kiy0w0
"""

import asyncio
import re

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded


"""
REF :- 
gem code - https://github.com/ChristopherBThai/Discord-OwO-Bot/blob/master/src/commands/commandList/shop/inventory.js
small numbers - https://github.com/ChristopherBThai/Discord-OwO-Bot/blob/master/src/commands/commandList/shop/util/shopUtil.js
"""


gem_tiers = {
    "common": ["051", "065", "072", "079"],
    "uncommon": ["052", "066", "073", "080"],
    "rare": ["053", "067", "074", "081"],
    "epic": ["054", "068", "075", "082"],
    "mythical": ["055", "069", "076", "083"],
    "legendary": ["056", "070", "077", "084"],
    "fabled": ["057", "071", "078", "085"],
}


def convert_small_numbers(small_number):
    numbers = {
        "⁰": "0",
        "¹": "1",
        "²": "2",
        "³": "3",
        "⁴": "4",
        "⁵": "5",
        "⁶": "6",
        "⁷": "7",
        "⁸": "8",
        "⁹": "9",
    }
    # Only convert superscript numbers, filter out other characters
    converted = ''.join(numbers.get(char, '') for char in small_number if char in numbers)
    # If no valid numbers found, return 0
    return int(converted) if converted else 0


def find_gems_available(message):

    available_gems = {
        "fabled": {"057": 0, "071": 0, "078": 0, "085": 0},  # fabled
        "legendary": {"056": 0, "070": 0, "077": 0, "084": 0},  # legendary
        "mythical": {"055": 0, "069": 0, "076": 0, "083": 0},  # mythical
        "epic": {"054": 0, "068": 0, "075": 0, "082": 0},  # epic
        "rare": {"053": 0, "067": 0, "074": 0, "081": 0},  # rare
        "uncommon": {"052": 0, "066": 0, "073": 0, "080": 0},  # uncommon
        "common": {"051": 0, "065": 0, "072": 0, "079": 0},  # common
        # hunt, emp, luck, special
    }
    """
    Example output:-
    [('050', '⁰⁷'), ('051', '⁰³')]
    """
    inv_numbers = re.findall(r"`(\d+)`.*?([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", message)
    for gem_id, small_number in inv_numbers:
        gem_count = convert_small_numbers(small_number)

        for _, gems in available_gems.items():
            if gem_id in gems:
                gems[gem_id] = gem_count
                break
    return available_gems


class Gems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.grouped_gems = None
        self.available_gems = None
        self.inventory_check = False
        self.gem_cmd = {
            "cmd_name": self.bot.alias["use"]["normal"],
            "cmd_arguments": "",
            "prefix": True,
            "checks": False,
            "id": "gems"
        }
        self.inv_cmd = {
            "cmd_name": self.bot.alias["inv"]["normal"],
            "prefix": True,
            "checks": True,
            "id": "inv"
        }

    def find_gems_to_use(self, available_gems):
        gem_type = {
            0: "huntGem",
            1: "empoweredGem",
            2: "luckyGem",
            3: "specialGem"
        }
        tier_order = ['fabled', 'legendary', 'mythical', 'epic', 'rare', 'uncommon', 'common']
        cnf = self.bot.settings_dict["autoUse"]["gems"]

        if cnf["order"]["lowestToHighest"]:
            tier_order.reverse()
            
        # SMART GEM MANAGER (QUEST CHECK)
        # Check if we have active 'special' gem quests
        force_special_gems = False
        try:
            quest_cog = self.bot.get_cog("Quest")
            if quest_cog and quest_cog.quest_detected:
                special_quest = quest_cog.quests.get("special", {})
                    if special_quest.get("target", 0) > special_quest.get("progress", 0) and not special_quest.get("completed", False):
                        force_special_gems = True
                        # Cannot await log here as function is sync
                        # print(f"💎 Smart Gem: Special Gem Quest Detected! Forcing use of special gems.")
        except Exception:
            pass # Fail silently if quest cog issue

        grouped_gem_list = []

        for tier in tier_order:
            if not cnf["tiers"][tier]:
                continue

            current_group = []
            for gem_id in gem_tiers[tier]:
                gem_index = gem_tiers[tier].index(gem_id)
                gem_type_key = gem_type[gem_index]
                
                # Check config normally, OR force if smart manager says so
                should_use = cnf["gemsToUse"].get(gem_type_key)
                
                if force_special_gems:
                    if gem_type_key == "specialGem":
                         should_use = True
                    # Optional: Disable other gems if we want to focus PURELY on special?
                    # Usually quests just want you to use special gems, doesn't matter if others are used too.
                    # But to save normal gems, we could prioritize special.
                    
                if should_use and available_gems[tier].get(gem_id, 0) > 0:
                    current_group.append(gem_id)

            if current_group:
                grouped_gem_list.append(current_group)

        return self.process_result(grouped_gem_list)


    def process_result(self, result):
        # Find the group with the highest number of items
        max_group = max(result, key=len, default=None)
        return max_group



    async def cog_load(self):
        if not self.bot.settings_dict["commands"]["hunt"]["enabled"] or not self.bot.settings_dict["autoUse"]["gems"]["enabled"]:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.gems"))
            except ExtensionNotLoaded:
                pass

    async def cog_unload(self):
        await self.bot.remove_queue(id="gems")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id or message.author.id != self.bot.owo_bot_id:
            return
        
        if "caught" in message.content:
            if self.bot.user_status["no_gems"]:
                return
            await self.bot.set_stat(False)
            self.inventory_check = True
            await self.bot.log(f"🔍 Checking inventory for gems...", "#00bcd4")
            await self.bot.put_queue(self.inv_cmd, priority=True)
        elif "'s Inventory ======**" in message.content:
            if self.inventory_check:
                await self.bot.remove_queue(id="inv")
                #if not self.available_gems:
                self.available_gems = find_gems_available(message.content)
                gems_list = self.find_gems_to_use(self.available_gems)

                self.gem_cmd["cmd_arguments"]=""
                if gems_list:
                    for i in gems_list:
                        self.gem_cmd["cmd_arguments"]+=f"{i[1:]} "
                    
                    # Log the gems being used
                    gems_used = self.gem_cmd["cmd_arguments"].strip()
                    await self.bot.log(f"💎 Using gems: {gems_used}", "#9c27b0")
                    self.bot.add_dashboard_log("gems", f"Using gems: {gems_used}", "info")
                    
                    # Reset no_gems status when gems are available
                    if self.bot.user_status["no_gems"]:
                        was_paused = self.bot.settings_dict.get("stopHuntingWhenNoGems", False)
                        self.bot.user_status["no_gems"] = False
                        await self.bot.log(f"✅ Gems available again!", "#51cf66")
                        self.bot.add_dashboard_log("gems", "Gems available", "success")
                        
                        # Auto-resume hunt and battle if stopHuntingWhenNoGems is enabled
                        if was_paused:
                            await self.bot.log(f"🔄 Resuming hunt and battle...", "#51cf66")
                            
                            # Resume hunt if enabled
                            if self.bot.settings_dict.get("commands", {}).get("hunt", {}).get("enabled", False):
                                hunt_cog = self.bot.get_cog('Hunt')
                                if hunt_cog:
                                    await asyncio.sleep(2)  # Small delay before resuming
                                    await self.bot.put_queue(hunt_cog.cmd)
                                    await self.bot.log(f"Hunt resumed", "#51cf66")
                                    self.bot.add_dashboard_log("hunt", "Hunt resumed - gems available", "success")
                            
                            # Resume battle if enabled
                            if self.bot.settings_dict.get("commands", {}).get("battle", {}).get("enabled", False):
                                battle_cog = self.bot.get_cog('Battle')
                                if battle_cog:
                                    await asyncio.sleep(2)  # Small delay before resuming
                                    await self.bot.put_queue(battle_cog.cmd)
                                    await self.bot.log(f"Battle resumed", "#51cf66")
                                    self.bot.add_dashboard_log("battle", "Battle resumed - gems available", "success")
                else:
                    if not self.bot.user_status["no_gems"]:
                        await self.bot.log(f"⚠️ No gems available!", "#ff9800")
                        self.bot.add_dashboard_log("gems", "No gems available", "warning")
                        self.bot.user_status["no_gems"] = True
                        
                        # Check if stopHuntingWhenNoGems is enabled
                        if self.bot.settings_dict.get("stopHuntingWhenNoGems", False):
                            await self.bot.log(f"🛑 stopHuntingWhenNoGems enabled - Hunt & Battle will pause", "#ff9800")
                            self.bot.add_dashboard_log("hunt", "Hunt & Battle pausing (no gems)", "warning")
                            
                await self.bot.put_queue(self.gem_cmd, priority=True)
                await self.bot.sleep_till(self.bot.settings_dict["defaultCooldowns"]["briefCooldown"])
                await self.bot.set_stat(True)
                self.inventory_check = False

async def setup(bot):
    await bot.add_cog(Gems(bot))
