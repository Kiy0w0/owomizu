import asyncio
import time
import re

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded


class AutoSell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sell_time = 0
        self.sell_triggers_this_hour = 0
        self.hour_reset_time = time.time() + 3600  # Reset counter every hour
        
        self.sell_cmd = {
            "cmd_name": "sell",
            "cmd_arguments": "",
            "prefix": True,
            "checks": True,
            "id": "autosell",
            "removed": False
        }

    async def cog_load(self):
        if not self.bot.settings_dict["autoSell"]["enabled"]:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.autosell"))
            except ExtensionNotLoaded:
                pass

    async def cog_unload(self):
        await self.bot.remove_queue(id="autosell")

    async def should_trigger_auto_sell(self):
        """Check if auto-sell should be triggered based on current conditions."""
        try:
            auto_sell_config = self.bot.settings_dict["autoSell"]
            
            # Check if auto-sell is enabled
            if not auto_sell_config["enabled"]:
                return False
            
            # Check if cash is below threshold
            current_balance = self.bot.user_status.get("balance", 0)
            threshold = auto_sell_config["triggerWhenCashBelow"]
            
            if current_balance >= threshold:
                return False
            
            # Reset hourly counter if needed
            current_time = time.time()
            if current_time > self.hour_reset_time:
                self.sell_triggers_this_hour = 0
                self.hour_reset_time = current_time + 3600
            
            # Check max triggers per hour
            if self.sell_triggers_this_hour >= auto_sell_config["maxTriggersPerHour"]:
                await self.bot.log(f"AutoSell: Max triggers per hour ({auto_sell_config['maxTriggersPerHour']}) reached", "#ff6b6b")
                return False
            
            # Check cooldown after last sell
            cooldown_min, cooldown_max = auto_sell_config["cooldownAfterSell"]
            time_since_last_sell = current_time - self.last_sell_time
            
            if time_since_last_sell < cooldown_min:
                return False
            
            return True
            
        except Exception as e:
            await self.bot.log(f"Error in should_trigger_auto_sell: {e}", "#c25560")
            return False

    async def trigger_auto_sell(self):
        """Trigger the auto-sell command."""
        try:
            auto_sell_config = self.bot.settings_dict["autoSell"]
            
            # Update sell command arguments
            self.sell_cmd["cmd_arguments"] = auto_sell_config["sellCommand"]
            
            # Log the auto-sell trigger
            current_balance = self.bot.user_status.get("balance", 0)
            await self.bot.log(f"AutoSell: Triggered! Balance: {current_balance} < {auto_sell_config['triggerWhenCashBelow']}", "#ffd43b")
            
            # Add dashboard log
            self.bot.add_dashboard_log("autosell", f"Auto-sell triggered (balance: {current_balance})", "warning")
            
            # Put sell command in queue
            await self.bot.put_queue(self.sell_cmd, priority=True)
            
            # Update counters
            self.last_sell_time = time.time()
            self.sell_triggers_this_hour += 1
            
            await self.bot.log(f"AutoSell: Sell command queued ({self.sell_triggers_this_hour}/{auto_sell_config['maxTriggersPerHour']} triggers this hour)", "#51cf66")
            
        except Exception as e:
            await self.bot.log(f"Error in trigger_auto_sell: {e}", "#c25560")

    async def check_balance_and_auto_sell(self):
        """Check balance and trigger auto-sell if needed."""
        if await self.should_trigger_auto_sell():
            await self.trigger_auto_sell()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.bot.cm.id and message.author.id == self.bot.owo_bot_id:
            
            # Listen for hunt/battle results that might reduce cash
            if ('you found:' in message.content.lower() or 
                "caught" in message.content.lower() or
                "goes into battle!" in message.content.lower()):
                
                # Small delay to let cash update from hunt/battle
                await asyncio.sleep(1)
                await self.check_balance_and_auto_sell()
            
            # Listen for failed command messages that might indicate low cash
            elif any(phrase in message.content.lower() for phrase in [
                "you don't have enough cowoncy",
                "insufficient funds",
                "not enough money",
                "you need at least"
            ]):
                await self.bot.log(f"AutoSell: Detected insufficient funds message", "#ff9500")
                await self.check_balance_and_auto_sell()
            
            # Listen for successful sell completion
            elif 'for a total of **<:cowoncy:416043450337853441>' in message.content.lower():
                if message.reference and message.reference.message_id:
                    try:
                        # Check if this was our auto-sell command
                        referenced_message = await message.channel.fetch_message(message.reference.message_id)
                        if referenced_message.author.id == self.bot.user.id and "sell all" in referenced_message.content.lower():
                            # Extract cowoncy earned from sell
                            cowoncy_match = re.search(r'for a total of \*\*<:cowoncy:\d+> ([\d,]+)', message.content)
                            if cowoncy_match:
                                earned = int(cowoncy_match.group(1).replace(',', ''))
                                await self.bot.log(f"AutoSell: Completed! Earned {earned:,} cowoncy", "#51cf66")
                                self.bot.add_dashboard_log("autosell", f"Auto-sell completed (+{earned:,} cowoncy)", "success")
                                
                                # Update balance
                                if self.bot.settings_dict["cashCheck"]:
                                    await self.bot.update_cash(earned)
                                
                                # Remove from queue
                                await self.bot.remove_queue(id="autosell")
                    except Exception as e:
                        await self.bot.log(f"Error processing auto-sell completion: {e}", "#c25560")


async def setup(bot):
    await bot.add_cog(AutoSell(bot))
