"""
Mizu OwO Bot - Rich Presence Cog
"""

from discord.ext import commands, tasks
import discord
import asyncio

STATUS_MAP = {
    "online":    discord.Status.online,
    "idle":      discord.Status.idle,
    "dnd":       discord.Status.dnd,
    "invisible": discord.Status.invisible,
}

class RichPresence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rpc_loop.start()

    def cog_unload(self):
        self.rpc_loop.cancel()

    def _get_discord_status(self):
        override = self.bot.global_settings_dict.get("discordStatus", "").strip().lower()
        if override and override in STATUS_MAP:
            return STATUS_MAP[override]

        if self.bot.command_handler_status["sleep"]:
            return discord.Status.idle
        elif not self.bot.command_handler_status["state"]:
            return discord.Status.dnd
        return discord.Status.online

    @tasks.loop(seconds=60)
    async def rpc_loop(self):
        if self.bot.global_settings_dict.get("offlineStatus", False):
            return
        try:
            activity = discord.Activity(
                type=discord.ActivityType.playing,
                name="OwOMIZU ON TOP",
            )
            await self.bot.change_presence(activity=activity, status=self._get_discord_status())
        except Exception as e:
            if self.bot.misc["debug"]["enabled"]:
                await self.bot.log(f"RPC Error: {e}", "#c25560")

    @rpc_loop.before_loop
    async def before_rpc(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RichPresence(bot))