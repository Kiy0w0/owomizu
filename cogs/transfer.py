import discord
from discord.ext import commands, tasks
import asyncio
import re

class AutoTransfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.transfer_check_loop.start()

    def cog_unload(self):
        self.transfer_check_loop.cancel()

    @tasks.loop(minutes=30)
    async def transfer_check_loop(self):
        """Periodically check if we need to transfer funds"""
        await self.bot.wait_until_ready()
        
        # Reload settings is handled by bot usually, but we access dict directly
        config = self.bot.settings_dict.get("autoTransfer", {})
        
        if not config.get("enabled", False):
            return

        target_id = config.get("destinationId")
        threshold = config.get("triggerAmount", 500000)
        
        if not target_id or target_id == 0:
            return

        # Don't transfer if this IS the target account
        if str(self.bot.user.id) == str(target_id):
            return

        # Check balance
        # We rely on 'owo cash' output or internal tracking if available
        # For safety, let's trigger a check
        await self.bot.send("owo cash")
        
        # Note: Actual transfer logic is triggered by on_message reading the cash balance
        # This loop just triggers the check to update balance info

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id:
            return
            
        # Parse "owo cash" response
        # Example: "User has 100,000 cowoncy"
        if message.author.id == self.bot.owo_bot_id and "cowoncy" in message.content.lower() and str(self.bot.user.id) in message.content:
            config = self.bot.settings_dict.get("autoTransfer", {})
            if not config.get("enabled", False):
                return
                
            target_id = config.get("destinationId")
            if not target_id or target_id == 0 or str(self.bot.user.id) == str(target_id):
                return

            # Extract amount using Regex
            # Matches: "User has 100,000 cowoncy" or "**User** has **100,000** cowoncy"
            match = re.search(r"has\s+(?:\*\*)?([0-9,]+)(?:\*\*)?\s+cowoncy", message.content)
            if match:
                amount_str = match.group(1).replace(",", "")
                amount = int(amount_str)
                
                threshold = config.get("triggerAmount", 500000)
                leave_amount = config.get("keepAmount", 50000) # Amount to keep in bot account
                
                transfer_amount = amount - leave_amount
                
                if transfer_amount >= threshold:
                    await asyncio.sleep(2) # Human delay
                    await self.bot.send(f"owo give {target_id} {transfer_amount}")
                    await self.bot.log(f"💸 Auto-Transfer: Sent {transfer_amount:,} to {target_id}", "green")
                    self.bot.add_dashboard_log("system", f"💸 Transferred {transfer_amount:,} cowoncy", "success")

async def setup(bot):
    await bot.add_cog(AutoTransfer(bot))
