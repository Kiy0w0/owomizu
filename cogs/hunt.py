   

import asyncio
import json
import re
from typing import Optional

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

try:
    with open("utils/emojis.json", 'r', encoding="utf-8") as file:
        emoji_dict = json.load(file)
except FileNotFoundError:
    print("The file emojis.json was not found.")
except json.JSONDecodeError:
    print("Failed to decode JSON from the file.")

def get_emoji_cost(text, emoji_dict=emoji_dict):
    pattern = re.compile(r"<a:[a-zA-Z0-9_]+:[0-9]+>|:[a-zA-Z0-9_]+:|[\U0001F300-\U0001F6FF\U0001F700-\U0001F77F]")
    emojis = pattern.findall(text)
    return [emoji_dict[char]["sell_price"] for char in emojis if char in emoji_dict]

def get_emoji_values(text):
    return sum(get_emoji_cost(text))

class Hunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._hunt_task: Optional[asyncio.Task] = None

    async def cog_load(self):
        if (
            not self.bot.settings_dict["commands"]["hunt"]["enabled"]
            or self.bot.settings_dict["defaultCooldowns"]["reactionBot"]["hunt_and_battle"]
        ):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.hunt"))
            except ExtensionNotLoaded:
                pass
        else:
            self._hunt_task = asyncio.create_task(self._hunt_loop())

    async def cog_unload(self):
        task = self._hunt_task
        if task is not None:
            task.cancel()

    def _get_cooldown(self):
        cd = self.bot.settings_dict["commands"]["hunt"]["cooldown"]
        if isinstance(cd, list):
            if cd[0] < 5:
                cd = [15, max(15, cd[1])]
        else:
            if cd < 5:
                cd = 15
        return cd

    def _get_cmd_name(self):
        return (
            self.bot.alias["hunt"]["shortform"]
            if self.bot.settings_dict["commands"]["hunt"]["useShortForm"]
            else self.bot.alias["hunt"]["alias"]
        )

    async def _hunt_loop(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(self.bot.random.uniform(1.5, 4.0))

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
                    await self.bot.log("Hunt paused - No gems available", "#ff9800")
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
                await self.bot.log(f"Error - {e}, in hunt _hunt_loop()", "#c25560")
                await asyncio.sleep(5)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.channel.id == self.bot.cm.id and message.author.id == self.bot.owo_bot_id:
                if 'you found:' in message.content.lower() or "caught" in message.content.lower():
                    msg_lines = message.content.splitlines()
                    sell_value = get_emoji_values(
                        msg_lines[0] if "caught" in message.content.lower() else msg_lines[1]
                    )
                    await self.bot.update_cash(sell_value - 5, assumed=True)
                    await self.bot.update_cash(5, reduce=True)
        except Exception as e:
            await self.bot.log(f"Error - {e}, During hunt on_message()", "#c25560")

async def setup(bot):
    await bot.add_cog(Hunt(bot))