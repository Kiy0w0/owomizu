   

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
        self.hour_reset_time = time.time() + 3600
        self.last_check_time = 0
        self.last_log_time = 0
        self.is_selling = False

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

    async def should_trigger_auto_sell(self, force_check=False):

        try:
            current_time = time.time()

            if not force_check and current_time - self.last_check_time < 10:
                return False

            self.last_check_time = current_time

            auto_sell_config = self.bot.settings_dict["autoSell"]

            if not auto_sell_config["enabled"]:
                return False

            if self.is_selling:
                return False

            try:
                queue_ids = [cmd.get("id", "") for cmd in self.bot.queue]
                if "sell" in queue_ids or "autosell" in queue_ids:
                    return False
            except:
                pass

            current_balance = self.bot.user_status.get("balance", 0)
            threshold = auto_sell_config["triggerWhenCashBelow"]

            if current_balance >= threshold:
                return False

            if current_time > self.hour_reset_time:
                self.sell_triggers_this_hour = 0
                self.hour_reset_time = current_time + 3600

            if self.sell_triggers_this_hour >= auto_sell_config["maxTriggersPerHour"]:
                if current_time - self.last_log_time > 1800:
                    await self.bot.log(f"AutoSell: Max triggers per hour ({auto_sell_config['maxTriggersPerHour']}) reached", "#ff6b6b")
                    self.last_log_time = current_time
                return False

            cooldown_min, cooldown_max = auto_sell_config["cooldownAfterSell"]
            time_since_last_sell = current_time - self.last_sell_time

            if time_since_last_sell < cooldown_min:
                return False

            return True

        except Exception as e:
            if current_time - self.last_log_time > 60:
                await self.bot.log(f"Error in should_trigger_auto_sell: {e}", "#c25560")
                self.last_log_time = current_time
            return False

    async def trigger_auto_sell(self):

        try:
            if self.is_selling:
                return

            self.is_selling = True
            auto_sell_config = self.bot.settings_dict["autoSell"]

            self.sell_cmd["cmd_arguments"] = auto_sell_config["sellCommand"]

            current_balance = self.bot.user_status.get("balance", 0)
            await self.bot.log(f"AutoSell: Triggered! Balance: {current_balance:,} < {auto_sell_config['triggerWhenCashBelow']:,}", "#ffd43b")

            self.bot.add_dashboard_log("autosell", f"Auto-sell triggered (balance: {current_balance:,})", "warning")

            await self.bot.put_queue(self.sell_cmd, priority=True)

            self.last_sell_time = time.time()
            self.sell_triggers_this_hour += 1

            asyncio.create_task(self.reset_selling_flag(30))

        except Exception as e:
            self.is_selling = False
            await self.bot.log(f"Error in trigger_auto_sell: {e}", "#c25560")

    async def reset_selling_flag(self, delay):

        await asyncio.sleep(delay)
        if self.is_selling:
            self.is_selling = False
            await self.bot.log("AutoSell: Reset selling flag (timeout protection)", "#ff9500")

    async def check_balance_and_auto_sell(self):

        if await self.should_trigger_auto_sell():
            await self.trigger_auto_sell()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.bot.cm.id and message.author.id == self.bot.owo_bot_id:

            if any(phrase in message.content.lower() for phrase in [
                "you don't have enough cowoncy",
                "insufficient funds", 
                "not enough money",
                "you need at least"
            ]):
                if await self.should_trigger_auto_sell(force_check=True):
                    await self.trigger_auto_sell()

            elif 'for a total of **<:cowoncy:416043450337853441>' in message.content:
                if message.reference and message.reference.message_id:
                    try:
                        referenced_message = await message.channel.fetch_message(message.reference.message_id)
                        if (referenced_message.author.id == self.bot.user.id and 
                            "sell" in referenced_message.content.lower()):

                            cowoncy_match = re.search(r'for a total of \*\*<:cowoncy:\d+> ([\d,]+)', message.content)
                            if cowoncy_match:
                                earned = int(cowoncy_match.group(1).replace(',', ''))

                                if self.is_selling:
                                    await self.bot.log(f"AutoSell: Completed! Earned {earned:,} cowoncy", "#51cf66")
                                    self.bot.add_dashboard_log("autosell", f"Auto-sell completed (+{earned:,} cowoncy)", "success")

                                if self.bot.settings_dict["cashCheck"]:
                                    await self.bot.update_cash(earned)

                                self.is_selling = False
                                await self.bot.remove_queue(id="autosell")

                    except Exception as e:
                        await self.bot.log(f"Error processing sell completion: {e}", "#c25560")

            elif ('you found:' in message.content.lower() or 
                  "caught" in message.content.lower() or
                  "goes into battle!" in message.content.lower()):

                current_time = time.time()
                if current_time - self.last_check_time > 30:
                    await asyncio.sleep(2)
                    await self.check_balance_and_auto_sell()

async def setup(bot):
    await bot.add_cog(AutoSell(bot))