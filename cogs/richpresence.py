"""
Mizu OwO Bot - Rich Presence Cog
Displays farming status & stats in real-time.
"""

from discord.ext import commands, tasks
import discord
import asyncio

class RichPresence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rpc_loop.start()

    def cog_unload(self):
        self.rpc_loop.cancel()

    @tasks.loop(seconds=60)
    async def rpc_loop(self):
        # Skip RPC if user forces offline mode
        if self.bot.global_settings_dict.get("offlineStatus", False):
            return

        try:
            # Fetch balance data
            balance = self.bot.user_status.get("balance", 0)
            earnings = self.bot.user_status.get("net_earnings", 0)
            
            # Determine status text
            if self.bot.command_handler_status["sleep"]:
                status_text = "Sleeping zZZ..."
                status_type = discord.Status.idle
            elif not self.bot.command_handler_status["state"]:
                status_text = "Paused ⏸️"
                status_type = discord.Status.dnd
            else:
                # Format number with commas (e.g. 1,000,000)
                bal_f = f"{balance:,}"
                status_text = f"OwOMIZU | 🪙 {bal_f}"
                status_type = discord.Status.online

            # Set Activity
            # type=3 is "Watching", type=0 is "Playing"
            # Replace '123456789' with your Application ID from Discord Dev Portal
            # Replace 'owo_logo' with the image key you uploaded to Art Assets
            
            activity = discord.Activity(
                type=discord.ActivityType.playing, 
                name=status_text,
                application_id=1468460406593945769, 
                assets={
                    "large_image": "waguri", 
                    "large_image_key": "waguri",
                    "large_text": "Mizu Auto Farm"
                },
                details=f"Balance: 🪙 {bal_f}",
                state="Auto Farming..."
            )
            
            await self.bot.change_presence(activity=activity, status=status_type)
            
        except Exception as e:
            # Silent error logging to avoid spam (unless debug is on)
            if self.bot.misc["debug"]["enabled"]:
                await self.bot.log(f"RPC Error: {e}", "#c25560")

    @rpc_loop.before_loop
    async def before_rpc(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RichPresence(bot))
