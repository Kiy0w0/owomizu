"""
Mizu OwO Bot
Copyright (C) 2025 MizuNetwork
Copyright (C) 2025 Kiy0w0
"""

import asyncio

from discord.ext import commands


class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._battle_task = None

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
        """Read cooldown from settings.json, enforce 5s minimum."""
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
        """
        Independent battle loop — sends command then sleeps for the cooldown
        configured in settings.json. No queue interference.
        """
        await self.bot.wait_until_ready()
        await asyncio.sleep(self.bot.random.uniform(4.0, 7.0))  # startup stagger (offset from hunt)

        while not self.bot.is_closed():
            try:
                # Wait while bot is paused / sleeping / captcha / rate-limited
                while (
                    not self.bot.command_handler_status["state"]
                    or self.bot.command_handler_status["sleep"]
                    or self.bot.command_handler_status["captcha"]
                    or self.bot.command_handler_status.get("rate_limited", False)
                ):
                    await asyncio.sleep(1.5)

                # Check stopHuntingWhenNoGems
                if (
                    self.bot.settings_dict.get("stopHuntingWhenNoGems", False)
                    and self.bot.user_status.get("no_gems", False)
                ):
                    await asyncio.sleep(10)
                    continue

                # Send battle command directly
                cmd_name = self._get_cmd_name()
                prefix = self.bot.settings_dict.get("setprefix", "owo ")
                silent = self.bot.global_settings_dict.get("silentTextMessages", False)
                await self.bot.cm.send(f"{prefix}{cmd_name}", silent=silent)

                # Sleep the configured cooldown — in 1s chunks to allow instant interrupt
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
                await self.bot.log(f"Error - {e}, in battle _battle_loop()", "#c25560")
                await asyncio.sleep(5)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.channel.id == self.bot.cm.id and message.author.id == self.bot.owo_bot_id:
                if message.embeds:
                    for embed in message.embeds:
                        if embed.author.name is not None and "goes into battle!" in embed.author.name.lower():
                            if message.reference is not None:
                                referenced = await message.channel.fetch_message(message.reference.message_id)
                                if not referenced.embeds and "You found a **weapon crate**!" in referenced.content:
                                    pass  # Allow
                                else:
                                    return
        except Exception as e:
            await self.bot.log(f"Error - {e}, During battle on_message()", "#c25560")


async def setup(bot):
    await bot.add_cog(Battle(bot))