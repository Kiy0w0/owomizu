import asyncio
import random

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded


def _build_argument(userids: list, ping: bool) -> str:
    if not userids:
        return ""
    chosen = random.choice(userids)
    return f"<@{chosen}>" if ping else str(chosen)


class Pray(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._ongoing = False
        self._startup = True

        self.pray_cmd = {
            "cmd_name": "pray",
            "cmd_arguments": None,
            "prefix": True,
            "checks": True,
            "id": "pray",
        }
        self.curse_cmd = {
            "cmd_name": "curse",
            "cmd_arguments": None,
            "prefix": True,
            "checks": True,
            "id": "pray",
        }

        self._pray_channel = None
        self._pray_channel_id = 0
        self._curse_channel = None
        self._curse_channel_id = 0

    async def _fetch_custom_channel(self, cmd: str, channel_id: int):
        cached_id = getattr(self, f"_{cmd}_channel_id")
        cached_ch = getattr(self, f"_{cmd}_channel")
        if cached_ch and cached_id == channel_id:
            return cached_ch
        try:
            ch = await self.bot.fetch_channel(channel_id)
            setattr(self, f"_{cmd}_channel", ch)
            setattr(self, f"_{cmd}_channel_id", channel_id)
            return ch
        except Exception as e:
            await self.bot.log(
                f"Failed to fetch custom pray/curse channel {channel_id}: {e}", "#c25560"
            )
            return None

    async def _send_direct(self, cmd: str, arg: str):
        while self.bot.command_handler_status.get("captcha", False):
            await asyncio.sleep(0.5)
        channel = getattr(self, f"_{cmd}_channel")
        if not channel:
            return
        prefix = self.bot.settings_dict.get("setprefix", "owo ")
        silent = self.bot.global_settings_dict.get("silentTextMessages", False)
        await channel.send(f"{prefix}{cmd} {arg}", silent=silent)
        await self.bot.log(f"{cmd} sent to custom channel #{channel.name}", "#4a3466")

    async def _cycle(self):
        self._ongoing = True
        enabled = [
            cmd for cmd in ("pray", "curse")
            if self.bot.settings_dict["commands"][cmd]["enabled"]
        ]
        cmd = random.choice(enabled)
        cnf = self.bot.settings_dict["commands"][cmd]

        if not self._startup:
            await self.bot.remove_queue(id="pray")
            await self.bot.sleep_till(cnf["cooldown"])
            self._cmd_obj(cmd)["checks"] = True
        else:
            await self.bot.sleep_till(
                self.bot.settings_dict["defaultCooldowns"]["shortCooldown"]
            )
            self._cmd_obj(cmd)["checks"] = False

        arg = _build_argument(cnf.get("userid", []), cnf.get("pingUser", False))
        self._cmd_obj(cmd)["cmd_arguments"] = arg

        custom = cnf.get("customChannel", {})
        if custom.get("enabled") and custom.get("channelId"):
            channel = await self._fetch_custom_channel(cmd, custom["channelId"])
            if channel:
                await self._send_direct(cmd, arg)
        else:
            await self.bot.put_queue(self._cmd_obj(cmd), priority=True)

        self._ongoing = False

        if custom.get("enabled") and custom.get("channelId"):
            self._startup = False
            await self._cycle()
        elif self._startup:
            await self.bot.sleep_till(
                self.bot.settings_dict["defaultCooldowns"]["shortCooldown"]
            )
            if self._startup:
                self._startup = False
                await self._cycle()

    def _cmd_obj(self, cmd: str) -> dict:
        return self.pray_cmd if cmd == "pray" else self.curse_cmd

    async def cog_load(self):
        pray_on = self.bot.settings_dict["commands"]["pray"]["enabled"]
        curse_on = self.bot.settings_dict["commands"]["curse"]["enabled"]
        reaction_mode = self.bot.settings_dict["defaultCooldowns"]["reactionBot"]["pray_and_curse"]

        if (not pray_on and not curse_on) or reaction_mode:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.pray"))
            except ExtensionNotLoaded:
                pass
        else:
            asyncio.create_task(self._cycle())

    async def cog_unload(self):
        await self.bot.remove_queue(id="pray")

    @commands.Cog.listener()
    async def on_message(self, message):
        if f"<@{self.bot.user.id}>" not in message.content:
            return
        if message.channel.id != self.bot.cm.id:
            return
        if message.author.id != self.bot.owo_bot_id:
            return

        pray_uid = self.bot.settings_dict["commands"]["pray"].get("userid", [])
        curse_uid = self.bot.settings_dict["commands"]["curse"].get("userid", [])

        pray_id_str = str(pray_uid[0]) if pray_uid else ""
        curse_id_str = str(curse_uid[0]) if curse_uid else ""

        triggers = [
            f"<@{self.bot.user.id}>** prays for **<@{pray_id_str}>**!",
            f"<@{self.bot.user.id}>** prays...",
            f"<@{self.bot.user.id}>** puts a curse on **<@{curse_id_str}>**!",
            f"<@{self.bot.user.id}>** is now cursed.",
            "Slow down and try the command again",
        ]
        if any(t in message.content for t in triggers):
            if not self._ongoing:
                await self.bot.log("pray/curse confirmed!", "#4a3466")
                self._startup = False
                await self._cycle()


async def setup(bot):
    await bot.add_cog(Pray(bot))