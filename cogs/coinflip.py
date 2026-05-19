import re
import asyncio

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

won_pattern = r"you won \*\*<:cowoncy:\d+> ([\d,]+)"
lose_pattern = r"spent \*\*<:cowoncy:\d+> ([\d,]+)"


class Coinflip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cmd = {
            "cmd_name": self.bot.alias["coinflip"]["normal"],
            "cmd_arguments": None,
            "prefix": True,
            "checks": True,
            "id": "coinflip",
        }
        self.turns_lost = 0
        self.exceeded_max_amount = False
        self.gamble_flags = {
            "goal_reached": False,
            "amount_exceeded": False,
            "no_balance": False,
        }

    async def cog_load(self):
        if not self.bot.settings_dict["gamble"]["coinflip"]["enabled"]:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.coinflip"))
            except ExtensionNotLoaded:
                pass
        else:
            asyncio.create_task(self.start_cf(startup=True))

    async def cog_unload(self):
        await self.bot.remove_queue(id="coinflip")

    async def start_cf(self, startup=False):
        cnf = self.bot.settings_dict["gamble"]["coinflip"]
        goal_cfg = self.bot.settings_dict["gamble"]["goalSystem"]
        try:
            if startup:
                await self.bot.sleep_till(self.bot.settings_dict["defaultCooldowns"]["briefCooldown"])
            else:
                await self.bot.remove_queue(id="coinflip")
                await self.bot.sleep_till(cnf["cooldown"])

            strategy = cnf.get("strategy", "martingale")

            if strategy == "safe" and self.turns_lost >= cnf.get("maxStreakSafe", 3):
                await self.bot.log(
                    f"Safe Mode: Lost {self.turns_lost} in a row. Stopping coinflip.", "#ff4444"
                )
                return

            if strategy in ("constant", "safe"):
                amount_to_gamble = int(cnf["startValue"])
            else:
                amount_to_gamble = int(cnf["startValue"] * (cnf["multiplierOnLose"] ** self.turns_lost))

            if goal_cfg["enabled"] and self.bot.gain_or_lose > goal_cfg["amount"]:
                if not self.gamble_flags["goal_reached"]:
                    self.gamble_flags["goal_reached"] = True
                    await self.bot.log(
                        f"Goal reached {self.bot.gain_or_lose}/{goal_cfg['amount']} — stopping coinflip.",
                        "#4a270c",
                    )
                return await self.start_cf()
            elif self.gamble_flags["goal_reached"]:
                self.gamble_flags["goal_reached"] = False

            if amount_to_gamble > self.bot.user_status["balance"] and self.bot.settings_dict["cashCheck"]:
                if not self.gamble_flags["no_balance"]:
                    self.gamble_flags["no_balance"] = True
                    await self.bot.log(
                        f"Next bet ({amount_to_gamble}) exceeds balance ({self.bot.user_status['balance']}) — pausing.",
                        "#4a270c",
                    )
                return await self.start_cf()
            elif self.gamble_flags["no_balance"]:
                await self.bot.log(f"Balance restored ({self.bot.user_status['balance']}) — resuming coinflip.", "#4a270c")
                self.gamble_flags["no_balance"] = False

            if self.bot.gain_or_lose + (self.bot.settings_dict["gamble"]["allottedAmount"] - amount_to_gamble) <= 0:
                if not self.gamble_flags["amount_exceeded"]:
                    self.gamble_flags["amount_exceeded"] = True
                    await self.bot.log(
                        f"Allotted amount ({self.bot.settings_dict['gamble']['allottedAmount']}) exceeded — pausing.",
                        "#4a270c",
                    )
                return await self.start_cf()
            elif self.gamble_flags["amount_exceeded"]:
                self.gamble_flags["amount_exceeded"] = False

            if amount_to_gamble > 250000:
                self.exceeded_max_amount = True
            else:
                self.cmd["cmd_arguments"] = str(amount_to_gamble)
                if cnf["options"]:
                    self.cmd["cmd_arguments"] += f" {self.bot.random.choice(cnf['options'])}"
                await self.bot.put_queue(self.cmd)

        except Exception as e:
            await self.bot.log(f"Error - {e}, in coinflip start_cf()", "#c25560")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.id != 408785106942164992:
            return
        if before.channel.id != self.bot.channel_id:
            return
        if self.exceeded_max_amount:
            return
        if "chose" not in after.content.lower():
            return
        try:
            if "and you lost it all... :c" in after.content.lower():
                self.turns_lost += 1
                match = int(re.search(lose_pattern, after.content).group(1).replace(",", ""))
                await self.bot.update_cash(match, reduce=True)
                self.bot.gain_or_lose -= match
                await self.bot.log(f"Lost {match} in coinflip. Net: {self.bot.gain_or_lose}", "#ffafaf")
                await self.start_cf()
                await self.bot.update_gamble_db("losses")
            else:
                won = int(re.search(won_pattern, after.content).group(1).replace(",", ""))
                lost = int(re.search(lose_pattern, after.content).group(1).replace(",", ""))
                profit = won - lost
                self.turns_lost = 0
                await self.bot.update_cash(profit)
                self.bot.gain_or_lose += profit
                await self.bot.log(f"Won {won} in coinflip. Net: {self.bot.gain_or_lose}", "#ffafaf")
                await self.start_cf()
                await self.bot.update_gamble_db("wins")
        except Exception as e:
            await self.bot.log(f"Error - {e}, in coinflip on_message_edit()", "#c25560")


async def setup(bot):
    await bot.add_cog(Coinflip(bot))
