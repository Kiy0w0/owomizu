import asyncio
import random
import time

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

from utils.watchdog import load_watchdog, should_restart


class Watchdog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._task = None
        self.cfg = load_watchdog()

    async def cog_load(self):
        if not self.cfg.get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.watchdog"))
            except ExtensionNotLoaded:
                pass
        else:
            self._task = asyncio.create_task(self._loop())
            await self.bot.log("Watchdog active, will restart on command stall", "#f59e0b")

    async def cog_unload(self):
        if self._task:
            self._task.cancel()

    async def _loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            interval = self.cfg.get("checkInterval", [60, 90])
            await asyncio.sleep(random.uniform(interval[0], interval[1]))

            last_ran = self.bot.cmds_state.get("global", {}).get("last_ran", 0)
            if should_restart(self.bot.command_handler_status, last_ran, time.time(), self.cfg):
                stall_mins = self.cfg.get("stallMinutes", 15)
                await self.bot.log(
                    f"Watchdog: no command ran in {stall_mins}+ min, restarting...", "#f59e0b"
                )
                self.bot.add_dashboard_log("system", "Watchdog restart on stall", "warn")
                await self.bot.close()
                return


async def setup(bot):
    await bot.add_cog(Watchdog(bot))
