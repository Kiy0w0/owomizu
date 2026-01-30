"""
Mizu OwO Bot -  Bank Cog
Copyright (C) 2025 MizuNetwork
"""

import asyncio
import time
import re
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_check = 0
        self.is_transferring = False
        
        self.cmd = {
            "cmd_name": "give",
            "cmd_arguments": "",
            "prefix": True,
            "checks": True,
            "id": "bank_transfer"
        }

    async def cog_load(self):
        if not self.bot.settings_dict.get("autoTransfer", {}).get("enabled", False):
            try:
                # Unload if not enabled to save resources
                asyncio.create_task(self.bot.unload_cog("cogs.bank"))
            except ExtensionNotLoaded:
                pass

    async def check_and_transfer(self):
        """Check balance and perform transfer if conditions met"""
        try:
            if self.is_transferring:
                return

            cnf = self.bot.settings_dict.get("autoTransfer", {})
            if not cnf.get("enabled", False):
                return

            # Throttling
            if time.time() - self.last_check < 30:
                return
            self.last_check = time.time()

            current_balance = self.bot.user_status.get("balance", 0)
            trigger_amount = cnf.get("triggerAmount", 500000)
            keep_amount = cnf.get("keepAmount", 50000)
            dest_id = cnf.get("destinationId", 0)

            if dest_id == 0 or dest_id == self.bot.user.id:
                # Invalid destination or self-transfer
                return

            if current_balance > trigger_amount:
                amount_to_transfer = current_balance - keep_amount
                
                if amount_to_transfer <= 0:
                    return

                self.is_transferring = True
                
                # Format: owo give <id> <amount>
                self.cmd["cmd_arguments"] = f"{dest_id} {amount_to_transfer}"
                
                await self.bot.log(f"🏦 Bank: Triggered! Balancing {current_balance:,} -> {keep_amount:,}. Moving {amount_to_transfer:,} to {dest_id}", "#ffd43b")
                self.bot.add_dashboard_log("bank", f"Auto-transfer triggered ({amount_to_transfer:,})", "warning")
                
                await self.bot.put_queue(self.cmd, priority=True)
                
                # Reset flag after delay
                asyncio.create_task(self.reset_transfer_flag())

        except Exception as e:
            self.is_transferring = False
            await self.bot.log(f"Error in Bank transfer: {e}", "#c25560")

    async def reset_transfer_flag(self):
        await asyncio.sleep(60)
        self.is_transferring = False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id:
            return
            
        # Hook into incoming messages to trigger checks
        # e.g. after hunting/battling or receiving cash
        if any(x in message.content.lower() for x in ["you found", "caught", "battle", "sent", "received"]):
            # Small delay to ensure balance is updated in updates_cash
            await asyncio.sleep(2) 
            await self.check_and_transfer()

        # Check for transfer success
        if "sent" in message.content.lower() and str(self.bot.user.id) in str(message.content): 
             # Rough check, relying on OwO's response usually "Sent X to Y"
             pass
        
        # Also check if we just updated cash via bot logic
        # (This listens to external messages, but bot updates cash internally too)

async def setup(bot):
    await bot.add_cog(Bank(bot))
