import asyncio
from typing import Optional

from discord.ext import commands


class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._battle_task: Optional[asyncio.Task] = None
        self._streak: int = 0

    async def cog_load(self):
        if (
            not self.bot.settings_dict["commands"]["battle"]["enabled"]
            or self.bot.settings_dict["defaultCooldowns"]["reactionBot"]["hunt_and_battle"]
        ):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.battle"))
            except Exception:
                pass
        else:
            self._battle_task = asyncio.create_task(self._battle_loop())

    async def cog_unload(self):
        if self._battle_task:
            self._battle_task.cancel()

    def _get_cooldown(self):
        cd = self.bot.settings_dict["commands"]["battle"]["cooldown"]
        if isinstance(cd, list):
            if cd[0] < 5:
                cd = [15, max(15, cd[1])]
        else:
            if cd < 5:
                cd = 15
        return cd

    def _get_cmd_name(self):
        return (
            self.bot.alias["battle"]["shortform"]
            if self.bot.settings_dict["commands"]["battle"]["useShortForm"]
            else self.bot.alias["battle"]["alias"]
        )

    async def _battle_loop(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(self.bot.random.uniform(4.0, 7.0))

        while not self.bot.is_closed():
            try:
                while (
                    not self.bot.command_handler_status["state"]
                    or self.bot.command_handler_status["sleep"]
                    or self.bot.command_handler_status["captcha"]
                    or self.bot.command_handler_status.get("rate_limited", False)
                ):
                    await asyncio.sleep(1.5)

                if (
                    self.bot.settings_dict.get("stopHuntingWhenNoGems", False)
                    and self.bot.user_status.get("no_gems", False)
                ):
                    await asyncio.sleep(10)
                    continue

                cmd_name = self._get_cmd_name()
                prefix = self.bot.settings_dict.get("setprefix", "owo ")
                silent = self.bot.global_settings_dict.get("silentTextMessages", False)
                await self.bot.cm.send(f"{prefix}{cmd_name}", silent=silent)

                cd = self._get_cooldown()
                sleep_time = (
                    self.bot.random.uniform(cd[0], cd[1])
                    if isinstance(cd, list)
                    else float(cd)
                )
                deadline = asyncio.get_event_loop().time() + sleep_time
                while asyncio.get_event_loop().time() < deadline:
                    if (
                        self.bot.command_handler_status["captcha"]
                        or self.bot.command_handler_status["sleep"]
                        or not self.bot.command_handler_status["state"]
                        or self.bot.command_handler_status.get("rate_limited", False)
                    ):
                        break
                    await asyncio.sleep(min(1.0, deadline - asyncio.get_event_loop().time()))

            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.bot.log(f"Error - {e}, in battle loop", "#c25560")
                await asyncio.sleep(5)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.channel.id != self.bot.cm.id:
                return
            if message.author.id != self.bot.owo_bot_id:
                return
            if not message.embeds:
                return

            battle_cfg = self.bot.settings_dict["commands"]["battle"]
            show_streak = battle_cfg.get("showStreakInConsole", False)
            notify_loss = battle_cfg.get("notifyStreakLoss", False)

            for embed in message.embeds:
                if embed.author and embed.author.name:
                    name_lower = embed.author.name.lower()
                    if "goes into battle!" in name_lower:
                        if message.reference:
                            try:
                                ref = await message.channel.fetch_message(
                                    message.reference.message_id
                                )
                                if not ref.embeds and "You found a **weapon crate**!" in ref.content:
                                    pass
                                else:
                                    return
                            except Exception:
                                pass

                    if f"{self.bot.user.name}" in embed.author.name:
                        if "won the battle" in name_lower or "won" in name_lower:
                            self._streak += 1
                            if show_streak:
                                await self.bot.log(
                                    f"Battle won! Streak: {self._streak}", "#51cf66"
                                )
                        elif "lost" in name_lower or "fled" in name_lower:
                            if notify_loss and self._streak > 0:
                                await self.bot.log(
                                    f"Battle streak lost at {self._streak}!", "#ff9800"
                                )
                                self.bot.add_dashboard_log(
                                    "battle", f"Streak lost at {self._streak}", "warning"
                                )
                            self._streak = 0

        except Exception as e:
            await self.bot.log(f"Error - {e}, in battle on_message", "#c25560")


async def setup(bot):
    await bot.add_cog(Battle(bot))