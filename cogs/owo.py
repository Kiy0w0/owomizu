"""
Mizu OwO Bot
Copyright (C) 2025 MizuNetwork
Copyright (C) 2025 Kiy0w0
"""

import asyncio

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded


class Owo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owo_ongoing = False

    async def send_owo(self, startup=False):
        cmd = {
            "cmd_name": "owo",
            "prefix": False,
            "checks": True,
            "id": "owo",
            "removed": False
        }
        if not startup:
            await self.bot.remove_queue(id="owo")
            self.owo_ongoing = True
            await self.bot.sleep_till(self.bot.settings_dict["commands"]["owo"]["cooldown"])
            self.owo_ongoing = False
        await self.bot.put_queue(cmd, quick=True)
            
    
    """gets executed when the cog is first loaded"""
    async def cog_load(self):
        if not self.bot.settings_dict["commands"]["owo"]["enabled"] or self.bot.settings_dict["defaultCooldowns"]["reactionBot"]["owo"]:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.owo"))
            except ExtensionNotLoaded:
                pass
        else:
            asyncio.create_task(self.send_owo(startup=True))

    @commands.Cog.listener()
    async def on_message(self, message):
        # Only respond to OwO bot messages, not our own messages
        if message.channel.id == self.bot.cm.id and message.author.id == self.bot.owo_bot_id:
            if "**OwO**" in message.content or "**UwU**" in message.content:
                if not self.owo_ongoing:
                    await self.send_owo()




async def setup(bot):
    await bot.add_cog(Owo(bot))