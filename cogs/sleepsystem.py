import asyncio
import random

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded


class SleepSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._task = None

    async def cog_load(self):
        cnf = self.bot.settings_dict.get("sleep", {})
        if not cnf.get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.sleepsystem"))
            except ExtensionNotLoaded:
                pass
        else:
            self._task = asyncio.create_task(self._loop())
            await self.bot.log("Sleep System active — bot will take natural breaks", "#60a5fa")

    async def cog_unload(self):
        if self._task:
            self._task.cancel()

    async def _loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            cnf = self.bot.settings_dict.get("sleep", {})
            check_cd = cnf.get("checkTime", [10, 20])
            await asyncio.sleep(random.uniform(check_cd[0], check_cd[1]) * 60)

            if not self.bot.command_handler_status.get("state", True):
                continue
            if self.bot.command_handler_status.get("captcha", False):
                continue

            freq = cnf.get("frequencyPercentage", 30)
            if random.randint(1, 100) > freq:
                continue

            sleep_range = cnf.get("sleeptime", [1, 10])
            duration_mins = random.uniform(sleep_range[0], sleep_range[1])
            duration_secs = duration_mins * 60

            await self.bot.log(
                f"Taking a natural break for {duration_mins:.1f} min...", "#60a5fa"
            )
            self.bot.command_handler_status["sleep"] = True
            self.bot.add_dashboard_log("system", f"Sleep break for {duration_mins:.1f}min", "info")
            await asyncio.sleep(duration_secs)
            self.bot.command_handler_status["sleep"] = False
            await self.bot.log("Break over, resuming!", "#51cf66")


async def setup(bot):
    await bot.add_cog(SleepSystem(bot))
