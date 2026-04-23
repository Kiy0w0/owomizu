import asyncio
import time

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

from utils.database import db


def _is_new_giveaway(created_ts: float, last_joined_ts: float | None) -> bool:
    if not last_joined_ts:
        return True
    return created_ts > last_joined_ts


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _last_joined_ts(self) -> float | None:
        val = await db.get_value(f"giveaway_last_{self.bot.user.id}")
        return float(val) if val else None

    def _mark_joined(self):
        db.set_value(f"giveaway_last_{self.bot.user.id}", str(time.time()))

    async def join_previous_giveaways(self):
        await self.bot.sleep_till(self.bot.settings_dict["defaultCooldowns"]["shortCooldown"])
        await self.bot.wait_until_ready()
        await self.bot.sleep_till(self.bot.settings_dict["defaultCooldowns"]["briefCooldown"])

        last_ts = await self._last_joined_ts()
        cnf = self.bot.settings_dict["giveawayJoiner"]

        for channel_id in cnf["channelsToJoin"]:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception:
                channel = None
            if not channel:
                await self.bot.log(f"Giveaway channel {channel_id} is invalid", "#ff5f00")
                continue

            await self.bot.set_stat(False)
            try:
                async for message in channel.history(limit=cnf["messageRangeToCheck"]):
                    if not message.embeds:
                        continue
                    for embed in message.embeds:
                        if embed.author and " A New Giveaway Appeared!" in embed.author.name:
                            created_ts = message.created_at.timestamp()
                            if not _is_new_giveaway(created_ts, last_ts):
                                continue
                            await self.bot.sleep_till(
                                self.bot.settings_dict["defaultCooldowns"]["briefCooldown"]
                            )
                            try:
                                btn = message.components[0].children[0]
                                if btn and not btn.disabled:
                                    await btn.click()
                                    await self.bot.log(
                                        f"Joined past giveaway in #{channel.name}", "#00d7af"
                                    )
                            except Exception:
                                pass
            except Exception as e:
                await self.bot.log(f"Error scanning giveaway history: {e}", "#c25560")
            finally:
                await self.bot.set_stat(True)

        self._mark_joined()

    async def cog_load(self):
        if self.bot.settings_dict.get("giveawayJoiner", {}).get("enabled", False):
            asyncio.create_task(self.join_previous_giveaways())
        else:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.giveaway"))
            except ExtensionNotLoaded:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        cnf = self.bot.settings_dict.get("giveawayJoiner", {})
        if message.channel.id not in cnf.get("channelsToJoin", []):
            return
        if not message.embeds:
            return

        for embed in message.embeds:
            if embed.author and " A New Giveaway Appeared!" in embed.author.name:
                last_ts = await self._last_joined_ts()
                if not _is_new_giveaway(message.created_at.timestamp(), last_ts):
                    return
                await self.bot.sleep_till(cnf.get("cooldown", [3, 8]))
                try:
                    btn = message.components[0].children[0]
                    if btn and not btn.disabled:
                        await btn.click()
                        await self.bot.log(
                            f"Joined giveaway in #{message.channel.name}", "#00d7af"
                        )
                        self._mark_joined()
                except Exception:
                    pass


async def setup(bot):
    await bot.add_cog(Giveaway(bot))