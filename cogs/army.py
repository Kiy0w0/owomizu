import asyncio
import re
import time

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

_EMBLEM_REGEX = re.compile(r"Today's remaining Broken Army Emblem\s*:\s*(\d+)", re.IGNORECASE)
_LIMIT_PHRASES = ("you can only find 15 emblems per day", "daily army limit")
_RESPONSE_WINDOW = 12.0


class ArmyFarmer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._task: asyncio.Task | None = None
        self._send_ts: float = 0.0
        self._cmd = {
            "cmd_name": "army",
            "prefix": True,
            "checks": True,
            "id": "army",
        }

    def _config(self):
        return self.bot.settings_dict.get("commands", {}).get("army", {})

    async def cog_load(self):
        if not self._config().get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.army"))
            except ExtensionNotLoaded:
                pass
            return
        self._task = asyncio.create_task(self._startup())

    async def cog_unload(self):
        if self._task:
            self._task.cancel()
        await self.bot.remove_queue(id="army")

    async def _startup(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(
            self.bot.random_float(
                self.bot.settings_dict["defaultCooldowns"]["shortCooldown"]
            )
        )
        await self._dispatch()

    async def _dispatch(self):
        await self.bot.remove_queue(id="army")
        self._send_ts = time.monotonic()
        await self.bot.put_queue(self._cmd)

    def _valid_response(self) -> bool:
        return self._send_ts > 0 and (time.monotonic() - self._send_ts) <= _RESPONSE_WINDOW

    async def _wait_for_reset(self):
        wait_seconds = self.bot.calc_time() + 10
        await self.bot.log(
            f"Army: daily emblems exhausted. Waiting {int(wait_seconds)}s for reset.",
            "#b5a642",
        )
        await asyncio.sleep(wait_seconds)
        await self._dispatch()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.cm.id:
            return
        if message.author.id != self.bot.owo_bot_id:
            return
        if not self._valid_response():
            return

        content = message.content

        match = _EMBLEM_REGEX.search(content)
        if match:
            remaining = int(match.group(1))
            await self.bot.log(f"Army: {remaining} emblems remaining.", "#b5a642")
            if remaining <= 0:
                asyncio.create_task(self._wait_for_reset())
            else:
                cooldown = self._config().get("cooldown", [30, 60])
                await asyncio.sleep(self.bot.random_float(cooldown))
                await self._dispatch()
            return

        content_lower = content.lower()
        if any(phrase in content_lower for phrase in _LIMIT_PHRASES):
            asyncio.create_task(self._wait_for_reset())


async def setup(bot):
    await bot.add_cog(ArmyFarmer(bot))
