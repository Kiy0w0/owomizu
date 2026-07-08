import asyncio
import re
import time

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

from utils.quest_helper.quest_types import QUEST_IDS

_RESPONSE_WINDOW = 12.0
_TITLE_RE = re.compile(r"\*\*\d+\.\s(.+?)\*\*")
_PROGRESS_RE = re.compile(r"Progress:\s*\[(\d+)/(\d+)\]")
_LOCKED_RE = re.compile(r"🔒 Locked")

_ACTIONS = {
    "owo": ("owo", "", False),
    "gamble": ("owo", "cf 1 h", False),
    "action_send": ("owo", "hug {uid}", False),
}


def _parse_first_active_quest(text: str) -> dict | None:
    titles = list(_TITLE_RE.finditer(text))
    if not titles:
        return None
    for i, match in enumerate(titles):
        title = match.group(1).strip()
        seg_start = match.end()
        seg_end = titles[i + 1].start() if i + 1 < len(titles) else len(text)
        segment = text[seg_start:seg_end]
        if _LOCKED_RE.search(segment):
            continue
        prog = _PROGRESS_RE.search(segment)
        if not prog:
            continue
        current, total = int(prog.group(1)), int(prog.group(2))
        if current >= total:
            continue
        return {"title": title, "progress_current": current, "progress_target": total}
    return None


class Quest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_quest = None
        self._send_ts = 0.0
        self._quest_cmd = {
            "cmd_name": "owo",
            "cmd_arguments": "quest",
            "prefix": False,
            "checks": True,
            "id": "quest_check",
        }

    def _config(self):
        return self.bot.settings_dict.get("questTracker", {})

    async def cog_load(self):
        if not self._config().get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.quest"))
            except ExtensionNotLoaded:
                pass
            return
        await self.bot.log("Quest Automation Loaded.", "#51cf66")
        asyncio.create_task(self._loop())

    async def _loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            while (
                self.bot.command_handler_status["captcha"]
                or not self.bot.command_handler_status["state"]
                or self.bot.command_handler_status["sleep"]
            ):
                await asyncio.sleep(10)
            try:
                await self._check_quest()
                if self.current_quest:
                    await self._solve(self.current_quest)
                await asyncio.sleep(self.bot.random.uniform(300, 600))
            except Exception as e:
                await self.bot.log(f"Quest loop error: {e}", "#c25560")
                await asyncio.sleep(60)

    async def _check_quest(self):
        self._send_ts = time.monotonic()
        self.current_quest = None
        await self.bot.put_queue(self._quest_cmd)
        await asyncio.sleep(6)

    def _valid_response(self) -> bool:
        return self._send_ts > 0 and (time.monotonic() - self._send_ts) <= _RESPONSE_WINDOW

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.owo_bot_id:
            return
        if message.channel.id != self.bot.cm.id:
            return
        if not self._valid_response():
            return
        if not message.embeds:
            return

        emb = message.embeds[0]
        text = ""
        if emb.description:
            text += emb.description + "\n"
        for field in emb.fields:
            text += f"{field.name}\n{field.value}\n"

        if "You finished all of your quests" in text:
            self._send_ts = 0.0
            return

        quest = _parse_first_active_quest(text)
        if quest:
            self.current_quest = quest
            self._send_ts = 0.0

    async def _solve(self, quest: dict):
        title = quest["title"].lower()
        remaining = quest["progress_target"] - quest["progress_current"]
        if remaining <= 0:
            return

        quest_data = QUEST_IDS.get(title)
        if not quest_data:
            return

        quest_id = quest_data["id"]
        action = _ACTIONS.get(quest_id)
        if not action:
            return

        cmd_name, cmd_args, use_prefix = action
        if "{uid}" in cmd_args:
            cmd_args = cmd_args.replace("{uid}", f"<@{self.bot.user.id}>")

        await self.bot.log(
            f"Quest: {title} ({quest['progress_current']}/{quest['progress_target']})",
            "#9b59b6",
        )

        cooldown = self.bot.settings_dict["defaultCooldowns"].get("shortCooldown", [10, 15])
        for _ in range(min(remaining, 5)):
            if self.bot.command_handler_status["captcha"]:
                break
            await self.bot.put_queue({
                "cmd_name": cmd_name,
                "cmd_arguments": cmd_args,
                "prefix": use_prefix,
                "checks": True,
                "id": "quest_action",
            })
            await asyncio.sleep(self.bot.random_float(cooldown))


async def setup(bot):
    await bot.add_cog(Quest(bot))
