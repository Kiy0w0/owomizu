"""
Mizu OwO Bot - Inventory Manager Cog
Copyright (C) 2025 MizuNetwork
"""

import asyncio
import time
import re
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checking = False
        self.last_check = 0
        
        self.inv_cmd = {
            "cmd_name": "inv",
            "cmd_arguments": "",
            "prefix": True,
            "checks": True,
            "id": "inventory_check"
        }
        
        self.equip_cmd = {
            "cmd_name": "equip",
            "cmd_arguments": "",
            "prefix": True,
            "checks": True,
            "id": "auto_equip"
        }

    async def cog_load(self):
        if not self.bot.settings_dict.get("autoEquip", {}).get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.inventory"))
            except ExtensionNotLoaded:
                pass
        else:
            asyncio.create_task(self.inventory_loop())

    async def inventory_loop(self):
        """Periodic inventory check loop"""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                cnf = self.bot.settings_dict.get("autoEquip", {})
                if not cnf.get("enabled", False):
                    break
                
                interval = cnf.get("interval_minutes", 60) * 60
                
                # Check if we should run
                if time.time() - self.last_check > interval:
                    self.checking = True
                    await self.bot.put_queue(self.inv_cmd)
                    self.last_check = time.time()
                
                await asyncio.sleep(60) # Check every minute if it's time
                
            except Exception as e:
                print(f"Error in inventory loop: {e}")
                await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id:
            return
            
        if not self.checking:
            return

        if message.author.id == self.bot.owo_bot_id and "Inventory" in message.content:
            try:
                # Parse inventory for weapons
                # Format example: `123 | Sword name (100 dmg)` 
                # Note: Format varies, this is a best-effort attempt
                
                # Find all weapons with DMG info
                # Regex looks for ID (digits) | Name (text) (Digits dmg)
                # Matches: "123456 | Super Sword (50 dmg)"
                weapons = re.findall(r"(\d+)\s*\|\s*(.*?)\s*\((\d+)\s*dmg\)", message.content)
                
                if not weapons:
                    # Try alternate format without bar or different spacing? 
                    # Providing a strict regex is risky, let's keep it simple.
                    self.checking = False
                    return

                best_weapon_id = 0
                max_dmg = -1
                current_equipped_dmg = -1
                
                for wid, name, dmg in weapons:
                    dmg = int(dmg)
                    # Check if this item line has an indicator it is equipped (often a star or separate field, but harder to parse in simple text)
                    # Current OwO text response doesn't always clearly mark equipped in the same list format easily without complex parsing.
                    # STRATEGY: Just Find ABSOLUTE BEST weapon in list.
                    
                    if dmg > max_dmg:
                        max_dmg = dmg
                        best_weapon_id = wid
                
                if best_weapon_id != 0:
                    # We found a best weapon.
                    # We blindly equip it. If it's already equipped, OwO usually just says "You equipped..." or "Already equipped".
                    # This is safe.
                    
                    self.equip_cmd["cmd_arguments"] = str(best_weapon_id)
                    await self.bot.log(f"⚔️ Auto-Equip: Found weapon ID {best_weapon_id} with {max_dmg} dmg!", "#a5d6a7")
                    self.bot.add_dashboard_log("inventory", f"Auto-equipping weapon {best_weapon_id} ({max_dmg} dmg)", "info")
                    
                    await self.bot.put_queue(self.equip_cmd, priority=True)
                
                self.checking = False
                
            except Exception as e:
                self.checking = False
                await self.bot.log(f"Error parsing inventory: {e}", "#c25560")

async def setup(bot):
    await bot.add_cog(Inventory(bot))
