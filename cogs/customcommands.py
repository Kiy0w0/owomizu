import asyncio
import time

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded


def _least_gap(values: list) -> dict | None:
    if len(values) < 2:
        return None
    best = {"min": values[0], "max": values[1], "diff": abs(values[1] - values[0])}
    for i in range(len(values) - 1):
        diff = abs(values[i + 1] - values[i])
        if diff < best["diff"]:
            best = {"min": values[i], "max": values[i + 1], "diff": max(diff, 1)}
    return best


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._tracker: list[dict] = []

    def _min_poll_interval(self) -> float:
        cooldowns = [
            item["cooldown"]
            for item in self.bot.settings_dict.get("customCommands", {}).get("commands", [])
            if item.get("enabled")
        ]
        if not cooldowns:
            return 5.0
        cooldowns.sort()
        gap = _least_gap(cooldowns)
        if gap:
            return float(min(gap["diff"], cooldowns[0]))
        return float(cooldowns[0])

    def _find_tracker(self, cmd_dict: dict):
        return [
            {"index": i, "data": d}
            for i, d in enumerate(self._tracker)
            if d.get("basedict") == cmd_dict
        ]

    async def _run(self, cmd_dict: dict, tracker_idx=None):
        cmd = {
            "cmd_name": cmd_dict["command"],
            "prefix": False,
            "checks": False,
            "id": "customcommand",
            "removed": False,
        }
        await self.bot.put_queue(cmd)
        entry = {"basedict": cmd_dict, "last_ran": time.monotonic()}
        if tracker_idx is not None:
            self._tracker[tracker_idx]["last_ran"] = time.monotonic()
        else:
            self._tracker.append(entry)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self._command_loop())

    async def _command_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            cmds = self.bot.settings_dict.get("customCommands", {}).get("commands", [])
            for cmd_dict in cmds:
                if not cmd_dict.get("enabled"):
                    continue
                results = self._find_tracker(cmd_dict)
                if not results:
                    await self._run(cmd_dict)
                else:
                    last_ran = results[0]["data"]["last_ran"]
                    elapsed = time.monotonic() - last_ran
                    if elapsed >= cmd_dict["cooldown"]:
                        await self._run(cmd_dict, results[0]["index"])
            poll = self._min_poll_interval()
            await asyncio.sleep(poll)

    async def cog_load(self):
        if not self.bot.settings_dict.get("customCommands", {}).get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.customcommands"))
            except ExtensionNotLoaded:
                pass
        else:
            await self.bot.log("Custom Commands loaded", "#a78bfa")


async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
