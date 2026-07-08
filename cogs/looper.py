import asyncio
import heapq
import itertools
import random
import string
import time

import aiohttp
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

_LOOPABLE = ["owo", "pray", "curse", "level"]


def _random_string(min_len: int, max_len: int) -> str:
    chars = string.ascii_lowercase + " "
    return "".join(random.choice(chars) for _ in range(random.randint(min_len, max_len)))


async def _fetch_quote(session: aiohttp.ClientSession) -> str | None:
    try:
        async with session.get("https://favqs.com/api/qotd", timeout=aiohttp.ClientTimeout(total=8)) as r:
            if r.status == 200:
                data = await r.json()
                return data.get("quote", {}).get("body")
    except Exception:
        return None


def _pray_arg(userids: list, ping: bool) -> str:
    if not userids:
        return ""
    uid = random.choice(userids)
    return f"<@{uid}>" if ping else str(uid)


class Looper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._heap: list = []
        self._counter = itertools.count()
        self._startup = True
        self._running = False
        self._task: asyncio.Task | None = None

    def _cfg(self, key: str) -> dict:
        commands_dict = self.bot.settings_dict.get("commands", {})
        mapping = {
            "owo": commands_dict.get("owo", {}),
            "pray": commands_dict.get("pray", {}),
            "curse": commands_dict.get("curse", {}),
            "level": commands_dict.get("lvlGrind", {}),
        }
        return mapping[key]

    def _reaction_cfg(self) -> dict:
        return self.bot.settings_dict.get("defaultCooldowns", {}).get("reactionBot", {})

    def _active_cmds(self) -> dict:
        rx = self._reaction_cfg()
        return {
            "owo": self._cfg("owo").get("enabled", False) and not rx.get("owo", False),
            "pray": self._cfg("pray").get("enabled", False) and not rx.get("pray_and_curse", False),
            "curse": self._cfg("curse").get("enabled", False) and not rx.get("pray_and_curse", False),
            "level": self._cfg("level").get("enabled", False),
        }

    def _next_run(self, cmd: str) -> float:
        now = time.monotonic()
        if self._startup and cmd in ("pray", "curse"):
            cd = self._cfg("owo").get("cooldown", [10, 12])
        else:
            cd = self._cfg(cmd).get("cooldown", [10, 60])
        return now + self.bot.random_float(cd)

    def _push(self, cmd: str):
        active = self._active_cmds()
        if not active.get(cmd, False):
            return
        entry = (self._next_run(cmd), next(self._counter), cmd)
        heapq.heappush(self._heap, entry)

    def _fill_missing(self):
        queued = {cmd for _, _, cmd in self._heap}
        for cmd in _LOOPABLE:
            if cmd not in queued:
                self._push(cmd)

    async def _build_owo_cmd(self) -> dict:
        return {
            "cmd_name": self.bot.alias.get("owo", {}).get("normal", "owo"),
            "prefix": False,
            "checks": False,
            "id": "owo",
        }

    async def _build_pray_curse_cmd(self, cmd: str) -> dict:
        cnf = self._cfg(cmd)
        arg = _pray_arg(cnf.get("userid", []), cnf.get("pingUser", False))
        custom = cnf.get("customChannel", {})
        return {
            "cmd_name": cmd,
            "cmd_arguments": arg,
            "prefix": True,
            "checks": False,
            "id": "pray",
            "channel": custom.get("channelId") if custom.get("enabled") else None,
        }

    async def _build_level_cmd(self) -> dict:
        cnf = self._cfg("level")
        if cnf.get("useQuoteInstead", False) and hasattr(self.bot, "session"):
            msg = await _fetch_quote(self.bot.session) or _random_string(
                cnf.get("minLengthForRandomString", 10),
                cnf.get("maxLengthForRandomString", 30),
            )
        else:
            msg = _random_string(
                cnf.get("minLengthForRandomString", 10),
                cnf.get("maxLengthForRandomString", 30),
            )
        return {
            "cmd_name": msg,
            "prefix": False,
            "checks": False,
            "id": "level",
        }

    async def _dispatch(self, cmd: str):
        if cmd == "owo":
            await self.bot.put_queue(await self._build_owo_cmd(), quick=True)
        elif cmd in ("pray", "curse"):
            await self.bot.put_queue(await self._build_pray_curse_cmd(cmd), priority=True)
        elif cmd == "level":
            await self.bot.put_queue(await self._build_level_cmd())
        self._startup = False

    async def _loop(self):
        await self.bot.wait_until_ready()
        self._fill_missing()

        while self._running:
            self._fill_missing()

            if not self._heap:
                await asyncio.sleep(1)
                continue

            next_ts, _, cmd = self._heap[0]
            wait = next_ts - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)

            if not self._running:
                break

            heapq.heappop(self._heap)
            await self._dispatch(cmd)
            self._push(cmd)

    async def cog_load(self):
        active = self._active_cmds()
        if not any(active.values()):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.looper"))
            except ExtensionNotLoaded:
                pass
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def cog_unload(self):
        self._running = False
        if self._task:
            self._task.cancel()
        for cmd_id in ("owo", "pray", "level"):
            await self.bot.remove_queue(id=cmd_id)


async def setup(bot):
    await bot.add_cog(Looper(bot))
