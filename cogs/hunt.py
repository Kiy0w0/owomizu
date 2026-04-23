import asyncio
import json
import re
from typing import Optional

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

try:
    with open("utils/emojis.json", "r", encoding="utf-8") as _f:
        _emoji_dict = json.load(_f)
except (FileNotFoundError, json.JSONDecodeError):
    _emoji_dict = {}

_EMOJI_PATTERN = re.compile(
    r"<a:[a-zA-Z0-9_]+:[0-9]+>|:[a-zA-Z0-9_]+:|[\U0001F300-\U0001F6FF\U0001F700-\U0001F77F]"
)

_RANK_ORDER = {
    "common": 1, "uncommon": 2, "rare": 3, "epic": 4,
    "mythical": 5, "gem": 6, "legendary": 7, "fabled": 8, "hidden": 9,
}


def _get_sell_value(text: str) -> int:
    return sum(
        _emoji_dict[e]["sell_price"]
        for e in _EMOJI_PATTERN.findall(text)
        if e in _emoji_dict
    )


def _parse_catches(text: str) -> list[dict]:
    results = []
    highest = {"rarity": "", "rank": 0}
    for emoji in _EMOJI_PATTERN.findall(text):
        data = _emoji_dict.get(emoji)
        if not data:
            continue
        rank = data.get("rank", "")
        rank_num = _RANK_ORDER.get(rank, 0)
        if emoji.startswith("<a:"):
            emoji_id = emoji.split(":")[2].rstrip(">")
            img_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif"
        else:
            emoji_id = emoji.strip(":")
            if emoji_id.endswith("2"):
                emoji_id = emoji_id[:-1]
            img_url = f"https://emojiapi.dev/api/v1/{emoji_id}/100.png"
        results.append({"rank": rank, "rank_num": rank_num, "emoji": emoji, "img_url": img_url})
        if rank_num > highest["rank"]:
            highest = {"rarity": rank, "rank": rank_num, "emoji": emoji}
    return results, highest


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
        if self._hunt_task:
            self._hunt_task.cancel()

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
                await self.bot.log(f"Error - {e}, in hunt loop", "#c25560")
                await asyncio.sleep(5)

    async def _maybe_send_animal_webhook(self, line: str):
        webhook_cfg = self.bot.global_settings_dict.get("webhook", {})
        if not webhook_cfg.get("enabled"):
            return
        animal_log_cfg = webhook_cfg.get("animal_log", {})
        if not animal_log_cfg.get("enabled"):
            return

        allowed_ranks = animal_log_cfg.get("rank", {})
        catches, highest = _parse_catches(line)
        if not catches:
            return

        filtered = [c for c in catches if allowed_ranks.get(c["rank"], False)]
        if not filtered:
            return

        if len(filtered) > 1:
            emoji_str = " ".join(c["emoji"] for c in filtered)
            await self.bot.webhookSender(
                title="Multiple rare animals caught!",
                desc=f"> <@{self.bot.user.id}> caught: {emoji_str}\n-# Best: {highest['emoji']} {highest['rarity']}",
                colors="#5B0B74",
                author_name="Hunt",
                author_img_url="https://cdn.discordapp.com/emojis/633448858432831488.gif",
            )
        else:
            c = filtered[0]
            await self.bot.webhookSender(
                title=f"Caught {c['emoji']} from hunt!",
                desc=f"> <@{self.bot.user.id}> caught a **{c['rank']}** {c['emoji']}.",
                colors="#5B0B74",
                img_url=c["img_url"],
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.channel.id != self.bot.cm.id:
                return
            if message.author.id != self.bot.owo_bot_id:
                return
            if "you found:" in message.content.lower() or "caught" in message.content.lower():
                lines = message.content.splitlines()
                target_line = lines[0] if "caught" in message.content.lower() else lines[1]
                sell_value = _get_sell_value(target_line)
                await self.bot.update_cash(sell_value - 5, assumed=True)
                await self.bot.update_cash(5, reduce=True)
                await self._maybe_send_animal_webhook(target_line)
        except Exception as e:
            await self.bot.log(f"Error - {e}, in hunt on_message", "#c25560")


async def setup(bot):
    await bot.add_cog(Hunt(bot))