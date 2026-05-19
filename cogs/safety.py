import asyncio
import re
import unicodedata

from discord.ext import commands


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return re.sub(r"[^a-z0-9]", "", text.lower())


_BAN_KEYWORDS = frozenset([
    "youhavebeenbanned",
    "bannedforbotting",
    "bannedformacros",
])

_CAPTCHA_KEYWORDS = frozenset([
    "areyouarealhuman",
    "verifythatyouarehuman",
    "pleasecomplete",
    "completeyourcaptcha",
    "tocheckthatyouareahuman",
])

_WARNING_PATTERN = re.compile(r"\((\d+)/(\d+)\)")


def _has_ban_keyword(normalized: str) -> bool:
    return any(kw in normalized for kw in _BAN_KEYWORDS)


def _has_captcha_keyword(normalized: str) -> bool:
    return any(kw in normalized for kw in _CAPTCHA_KEYWORDS)


def _parse_warning_counter(text: str):
    m = _WARNING_PATTERN.search(text)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


class Safety(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        import time as _t
        self.start_time = _t.time()
        self.is_safety_paused = False
        self.default_run_minutes = 120
        self.default_pause_minutes = 15

    async def cog_load(self):
        if not self.bot.settings_dict.get("safety", {}).get("enabled", False):
            await self.bot.log("Safety System disabled (enable in settings for anti-ban)", "#9dc3f5")
        else:
            await self.bot.log("Safety System Loaded", "#51cf66")
            self.bot.loop.create_task(self.safety_loop())

    async def safety_loop(self):
        import time as _t
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                safety_conf = self.bot.settings_dict.get("safety", {})
                if not safety_conf.get("enabled", False):
                    await asyncio.sleep(60)
                    continue

                work_schedule = safety_conf.get("workSchedule", {"enabled": False})
                if work_schedule.get("enabled", False):
                    import datetime
                    now = datetime.datetime.now()
                    current_hour = now.hour
                    start_hour = work_schedule.get("startHour", 7)
                    end_hour = work_schedule.get("endHour", 23)

                    if start_hour <= end_hour:
                        is_working = start_hour <= current_hour < end_hour
                    else:
                        is_working = current_hour >= start_hour or current_hour < end_hour

                    if not is_working:
                        if not self.bot.command_handler_status["sleep"]:
                            await self.bot.log(f"Schedule: Sleeping until {start_hour}:00", "#95a5a6")
                            self.bot.command_handler_status["sleep"] = True
                            self.bot.add_dashboard_log("system", "Sleeping (Schedule)", "warning")
                        await asyncio.sleep(60)
                        continue
                    else:
                        if self.bot.command_handler_status["sleep"] and not self.is_safety_paused:
                            await self.bot.log("Schedule: Resuming farm", "#f1c40f")
                            self.bot.command_handler_status["sleep"] = False
                            self.start_time = _t.time()

                run_duration = safety_conf.get("runTimeMinutes", self.default_run_minutes) * 60
                if (_t.time() - self.start_time) >= run_duration:
                    self.is_safety_paused = True
                    self.bot.command_handler_status["sleep"] = True
                    base_sleep = safety_conf.get("sleepTimeMinutes", self.default_pause_minutes) * 60
                    variance = base_sleep * 0.2
                    actual_sleep = base_sleep + self.bot.random.uniform(-variance, variance)
                    await self.bot.log(f"Safety Pause: {int(actual_sleep/60)} min break.", "#e67e22")
                    self.bot.add_dashboard_log("system", "Starting Safety Sleep", "warning")
                    await asyncio.sleep(actual_sleep)
                    self.start_time = _t.time()
                    self.is_safety_paused = False
                    self.bot.command_handler_status["sleep"] = False
                    await self.bot.log("Safety Pause: Resumed farming!", "#2ecc71")
                    self.bot.add_dashboard_log("system", "Resumed from Safety Sleep", "success")

                await asyncio.sleep(60)
            except Exception as e:
                await self.bot.log(f"Safety Loop Error: {e}", "#c25560")
                await asyncio.sleep(60)

    async def _send_security_alert(self, title: str, description: str):
        try:
            await self.bot.webhookSender(
                title=title,
                desc=description,
                colors="#d70000",
                author_name="Security Alert",
            )
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        import time as _t

        safety_conf = self.bot.settings_dict.get("safety", {})
        if not safety_conf.get("enabled", False):
            return

        if message.guild and message.channel.id not in self.bot.list_channel:
            return

        content_lower = message.content.lower()

        auto_stop_conf = safety_conf.get("autoStop", {})
        if auto_stop_conf.get("enabled", False):
            for trigger in [t.lower() for t in auto_stop_conf.get("delayTriggers", [])]:
                if trigger in content_lower:
                    delay_duration = auto_stop_conf.get("delayDuration", 300)
                    await self.bot.log(f"Cooldown Triggered: '{trigger}' — pausing {delay_duration}s", "#f39c12")
                    self.bot.add_dashboard_log("system", f"Temporary Pause: {trigger}", "warning")
                    self.bot.loop.create_task(self.temporary_sleep(delay_duration))
                    return

            for trigger in [t.lower() for t in auto_stop_conf.get("triggers", [])]:
                if trigger in content_lower:
                    await self.bot.log(f"AUTO-STOP: '{trigger}' detected!", "#e74c3c")
                    self.bot.command_handler_status["state"] = False
                    self.bot.add_dashboard_log("system", f"Auto-Stop: {trigger}", "critical")
                    return

        if message.author.id != self.bot.owo_bot_id:
            return
        if not (str(self.bot.user.id) in message.content or any(m.id == self.bot.user.id for m in message.mentions)):
            return

        embed_text = ""
        for e in message.embeds:
            parts = [e.title or "", e.description or ""]
            if e.footer:
                parts.append(e.footer.text or "")
            embed_text += " ".join(parts)

        full_text = f"{message.content} {embed_text}"
        normalized = _normalize(full_text)

        if _has_ban_keyword(normalized):
            self.bot.command_handler_status["state"] = False
            await self.bot.log("BAN DETECTED! Bot stopped.", "#d70000")
            self.bot.add_dashboard_log("system", "Ban detected — bot stopped", "critical")
            await self._send_security_alert("BAN DETECTED", f"Message:\n{message.content[:500]}")
            return

        warning = _parse_warning_counter(full_text)
        if warning and _has_captcha_keyword(normalized):
            current, maximum = warning
            self.bot.command_handler_status["captcha"] = True
            await self.bot.log(f"CAPTCHA WARNING ({current}/{maximum}) detected!", "#d70000")
            self.bot.add_dashboard_log("system", f"Captcha warning {current}/{maximum}", "critical")
            await self._send_security_alert(
                f"CAPTCHA WARNING ({current}/{maximum})",
                f"Message:\n{message.content[:500]}",
            )
            return

    async def temporary_sleep(self, duration):
        import time as _t
        if self.bot.command_handler_status["sleep"]:
            return
        self.bot.command_handler_status["sleep"] = True
        await asyncio.sleep(duration)
        safety_conf = self.bot.settings_dict.get("safety", {})
        work_schedule = safety_conf.get("workSchedule", {"enabled": False})
        if work_schedule.get("enabled", False):
            import datetime
            now = datetime.datetime.now()
            current_hour = now.hour
            start = work_schedule.get("startHour", 7)
            end = work_schedule.get("endHour", 23)
            if start <= end:
                is_working = start <= current_hour < end
            else:
                is_working = current_hour >= start or current_hour < end
            if not is_working:
                await self.bot.log("Cooldown expired, but still sleeptime. Staying asleep.", "#95a5a6")
                return
        self.bot.command_handler_status["sleep"] = False
        await self.bot.log("Cooldown expired. Resuming!", "#2ecc71")


async def setup(bot):
    await bot.add_cog(Safety(bot))