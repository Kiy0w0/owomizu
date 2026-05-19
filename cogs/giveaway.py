import asyncio
import json
import os
import time

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded


def is_already_joined(message_id: int, joined_ids: set) -> bool:
    return message_id in joined_ids


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._joined_ids: set = set()
        self._db_path: str = ""

    def _get_db_path(self) -> str:
        if self._db_path:
            return self._db_path
        username = getattr(self.bot, "user", None)
        uid = str(username.id) if username else "unknown"
        self._db_path = os.path.join("config", f"giveaway_ids_{uid}.json")
        return self._db_path

    def _load_ids(self):
        path = self._get_db_path()
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    self._joined_ids = set(data.get("joined_ids", []))
        except Exception:
            self._joined_ids = set()

    def _save_ids(self):
        path = self._get_db_path()
        if len(self._joined_ids) > 200:
            self._joined_ids = set(list(self._joined_ids)[-200:])
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump({"joined_ids": list(self._joined_ids)}, f)
        except Exception as e:
            self.bot.loop.create_task(
                self.bot.log(f"Giveaway: failed to save IDs: {e}", "#c25560")
            )

    async def _try_join(self, message):
        cnf = self.bot.settings_dict.get("giveawayJoiner", {})
        if not cnf.get("enabled", False):
            return
        if message.channel.id not in cnf.get("channelsToJoin", []):
            return
        if not message.embeds:
            return

        for embed in message.embeds:
            if not (embed.author and " A New Giveaway Appeared!" in embed.author.name):
                continue
            if is_already_joined(message.id, self._joined_ids):
                return
            await self.bot.sleep_till(cnf.get("cooldown", [3, 8]))
            try:
                btn = message.components[0].children[0]
                if btn and not btn.disabled:
                    await btn.click()
                    self._joined_ids.add(message.id)
                    self._save_ids()
                    await self.bot.log(
                        f"Joined giveaway in #{message.channel.name}", "#00d7af"
                    )
            except Exception:
                pass

    async def _startup_scan(self):
        await self.bot.wait_until_ready()
        await self.bot.sleep_till(self.bot.settings_dict["defaultCooldowns"]["shortCooldown"])
        self._load_ids()
        cnf = self.bot.settings_dict.get("giveawayJoiner", {})
        if not cnf.get("enabled", False):
            return
        for channel_id in cnf.get("channelsToJoin", []):
            try:
                channel = await self.bot.fetch_channel(channel_id)
                if not channel:
                    continue
                await self.bot.set_stat(False)
                try:
                    async for msg in channel.history(limit=cnf.get("messageRangeToCheck", 10)):
                        await self._try_join(msg)
                except Exception:
                    pass
                finally:
                    await self.bot.set_stat(True)
            except Exception as e:
                await self.bot.log(f"Giveaway scan error ch {channel_id}: {e}", "#c25560")

    async def cog_load(self):
        cnf = self.bot.settings_dict.get("giveawayJoiner", {})
        if cnf.get("enabled", False):
            asyncio.create_task(self._startup_scan())
        else:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.giveaway"))
            except ExtensionNotLoaded:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        await self._try_join(message)


async def setup(bot):
    await bot.add_cog(Giveaway(bot))