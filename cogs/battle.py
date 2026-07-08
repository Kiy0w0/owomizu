import asyncio
import time

from discord.ext import commands


class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._streak: int = 0
        self._send_ts: float = 0.0
        self._cmd = {
            "cmd_name": "",
            "prefix": True,
            "checks": True,
            "id": "battle",
        }

    def _cfg(self):
        return self.bot.settings_dict["commands"]["battle"]

    def _cmd_name(self) -> str:
        return (
            self.bot.alias["battle"]["shortform"]
            if self._cfg().get("useShortForm", True)
            else self.bot.alias["battle"]["normal"]
        )

    async def cog_load(self):
        if (
            not self._cfg()["enabled"]
            or self.bot.settings_dict["defaultCooldowns"]["reactionBot"]["hunt_and_battle"]
        ):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.battle"))
            except Exception:
                pass
        else:
            self._cmd["cmd_name"] = self._cmd_name()
            asyncio.create_task(self.bot.put_queue(self._cmd))

    async def cog_unload(self):
        await self.bot.remove_queue(id="battle")

    async def _dispatch(self):
        await self.bot.remove_queue(id="battle")
        cd = self._cfg().get("cooldown", [15, 16])
        sleep_time = self.bot.random_float(cd)
        await asyncio.sleep(sleep_time)
        self._cmd["cmd_name"] = self._cmd_name()
        self._send_ts = time.monotonic()
        await self.bot.put_queue(self._cmd)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.channel.id != self.bot.cm.id:
                return
            if message.author.id != self.bot.owo_bot_id:
                return
            if not message.embeds:
                return

            cfg = self._cfg()
            show_streak = cfg.get("showStreakInConsole", False)
            notify_loss = cfg.get("notifyStreakLoss", False)

            for embed in message.embeds:
                if not (embed.author and embed.author.name):
                    continue

                author_name = embed.author.name
                name_lower = author_name.lower()

                if "goes into battle!" not in name_lower:
                    continue

                if message.reference:
                    try:
                        ref = await message.channel.fetch_message(message.reference.message_id)
                        if not ref.embeds and "You found a **weapon crate**!" in ref.content:
                            pass
                        else:
                            return
                    except Exception:
                        pass

                if self.bot.user.name not in author_name:
                    continue

                if embed.footer and embed.footer.text:
                    footer = embed.footer.text
                    if show_streak:
                        await self.bot.log(footer, "#292252")
                    if "lost" in footer.lower() or "fled" in footer.lower():
                        if notify_loss and self._streak > 0:
                            await self.bot.log(
                                f"Battle streak lost at {self._streak}!", "#ff9800"
                            )
                            self.bot.add_dashboard_log(
                                "battle", f"Streak lost at {self._streak}", "warning"
                            )
                        self._streak = 0
                    else:
                        self._streak += 1
                        if show_streak:
                            await self.bot.log(f"Battle streak: {self._streak}", "#51cf66")

                asyncio.create_task(self._dispatch())

        except Exception as e:
            await self.bot.log(f"Error - {e}, in battle on_message", "#c25560")


async def setup(bot):
    await bot.add_cog(Battle(bot))