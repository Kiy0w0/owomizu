import asyncio
import json
import re
import time

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

from cogs import comp

_RESPONSE_WINDOW = 15.0
_UNREAD_RE = re.compile(r"have \*\*\d+\*\* unread mail")


def _is_unread_notification(content: str, display_name: str) -> bool:
    return display_name in content and bool(_UNREAD_RE.search(content))


def _is_mailbox_header(content: str, user_id: int) -> bool:
    return f"<@{user_id}>'s Mailbox" in content


def _is_unclaimed(accessory) -> bool:
    return not getattr(accessory, "disabled", True)


def _has_next_page(buttons) -> bool:
    for btn in buttons:
        if getattr(btn, "custom_id", None) == "noop":
            parts = (btn.label or "").replace("/", " ").split()
            if len(parts) == 2:
                try:
                    return int(parts[0]) < int(parts[1])
                except ValueError:
                    pass
    return False


class Mail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._task = None
        self._send_ts = 0.0
        self._mailbox_msg_id = 0
        self._cmd = {
            "cmd_name": "mail",
            "cmd_arguments": None,
            "prefix": True,
            "checks": True,
            "id": "mail",
        }

    def _config(self):
        return self.bot.settings_dict.get("commands", {}).get("mail", {})

    async def cog_load(self):
        if not self._config().get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.mail"))
            except ExtensionNotLoaded:
                pass
            return
        self._task = asyncio.create_task(self._startup())

    async def cog_unload(self):
        if self._task:
            self._task.cancel()
        await self.bot.remove_queue(id="mail")

    async def _startup(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(
            self.bot.random_float(
                self.bot.settings_dict["defaultCooldowns"]["shortCooldown"]
            )
        )
        await self._dispatch()

    async def _dispatch(self):
        await self.bot.remove_queue(id="mail")
        self._send_ts = time.monotonic()
        await self.bot.put_queue(self._cmd)

    def _valid_response(self) -> bool:
        return self._send_ts > 0 and (time.monotonic() - self._send_ts) <= _RESPONSE_WINDOW

    async def _get_guild_id(self, data: dict, channel_id: int):
        gid = data.get("guild_id")
        if not gid:
            try:
                ch = self.bot.get_channel(channel_id)
                if ch and ch.guild:
                    gid = ch.guild.id
            except Exception:
                pass
        return gid

    @commands.Cog.listener()
    async def on_socket_raw_receive(self, msg):
        if '"MESSAGE_CREATE"' not in msg and '"MESSAGE_UPDATE"' not in msg:
            return
        try:
            parsed = json.loads(msg)
            event = parsed.get("t")
            if event not in ("MESSAGE_CREATE", "MESSAGE_UPDATE"):
                return

            data = parsed.get("d", {})
            if data.get("author", {}).get("id") != str(self.bot.owo_bot_id):
                return
            if int(data.get("channel_id", 0)) != self.bot.cm.id:
                return

            message = comp.message.get_message_obj(data)
            if not message.components:
                return

            msg_id = int(data.get("id", 0))

            if event == "MESSAGE_CREATE":
                await self._on_create(message, data, msg_id)
            elif event == "MESSAGE_UPDATE" and msg_id == self._mailbox_msg_id:
                await self._process_mailbox(message, data)

        except Exception as e:
            await self.bot.log(f"Mail: {e}", "#c25560")

    async def _on_create(self, message, data: dict, msg_id: int):
        for component in message.components:
            if component.component_name == "section":
                inner = component.components or []
                if inner and inner[0].component_name == "text_display":
                    content = inner[0].content or ""
                    if _is_unread_notification(content, self.bot.user.display_name):
                        await self._handle_notification(component, data)
                        return

            if component.component_name == "text_display":
                if _is_mailbox_header(component.content or "", self.bot.user.id):
                    if self._valid_response():
                        self._mailbox_msg_id = msg_id
                        await self._process_mailbox(message, data)
                    return

    async def _handle_notification(self, section, data: dict):
        await self.bot.log("Mail detected, claiming...", "#4c9d9e")
        btn = next(
            (b for b in (section.buttons or []) if getattr(b, "custom_id", None) == "show_mail"),
            None,
        )
        if not btn:
            return
        ch_id = int(data.get("channel_id", 0))
        gid = await self._get_guild_id(data, ch_id)
        if not gid or self.bot.command_handler_status["captcha"]:
            return
        await asyncio.sleep(self.bot.random_float([0.8, 1.5]))
        self._send_ts = time.monotonic()
        await btn.click(self.bot.ws.session_id, self.bot.local_headers, gid)

    async def _process_mailbox(self, message, data: dict):
        gid = await self._get_guild_id(data, int(data.get("channel_id", 0)))
        if not gid:
            return

        for component in message.components:
            if component.component_name != "section":
                continue
            acc = getattr(component, "accessory", None)
            if not acc or acc.component_name != "button":
                continue
            if not _is_unclaimed(acc):
                continue
            if self.bot.command_handler_status["captcha"]:
                return
            await asyncio.sleep(self.bot.random_float([0.8, 1.5]))
            await acc.click(self.bot.ws.session_id, self.bot.local_headers, gid)
            await self.bot.log("Mail claimed.", "#4c9d9e")
            return

        if _has_next_page(message.buttons):
            nxt = next(
                (b for b in message.buttons if "next" in (b.custom_id or "").lower()),
                None,
            )
            if nxt and not self.bot.command_handler_status["captcha"]:
                await asyncio.sleep(self.bot.random_float([1.0, 2.0]))
                await nxt.click(self.bot.ws.session_id, self.bot.local_headers, gid)
            return

        self._mailbox_msg_id = 0
        cooldown = self._config().get("cooldown", [3600, 7200])
        await asyncio.sleep(self.bot.random_float(cooldown))
        await self._dispatch()


async def setup(bot):
    await bot.add_cog(Mail(bot))
