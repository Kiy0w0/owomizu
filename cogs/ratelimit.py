import asyncio
import time

from discord.ext import commands


class RateLimitHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._rate_limit_count = 0
        self._last_rate_limit = 0
        self._rate_limit_window = 60
        self._pause_threshold = 3
        self._paused = False
        self._total_rate_limits = 0
        self._idle_triggered = False

    @commands.Cog.listener()
    async def on_http_ratelimit(self, payload):
        now = time.time()
        retry_after = getattr(payload, "retry_after", 5.0)
        is_global = getattr(payload, "is_global", False)

        self._total_rate_limits += 1

        if now - self._last_rate_limit > self._rate_limit_window:
            self._rate_limit_count = 0

        self._rate_limit_count += 1
        self._last_rate_limit = now

        scope = "🌐 GLOBAL" if is_global else "📦 Bucket"
        await self.bot.log(
            f"⚡ Rate Limited! ({scope}) - Retry after {retry_after:.1f}s "
            f"[{self._rate_limit_count}/{self._pause_threshold} in window]",
            "#ff6b6b",
        )
        self.bot.add_dashboard_log(
            "system",
            f"Rate limit hit ({self._rate_limit_count}x) - retry after {retry_after:.1f}s",
            "warning",
        )

        if self._rate_limit_count >= self._pause_threshold and not self._paused:
            await self._auto_pause()

    async def _auto_pause(self):
        self._paused = True

        base_pause = 30
        severity_multiplier = min(self._rate_limit_count, 10)
        pause_duration = base_pause * severity_multiplier

        await self.bot.log(
            f"🛑 Rate Limit Protection: Auto-pausing for {pause_duration}s "
            f"({self._rate_limit_count} rate limits in {self._rate_limit_window}s window)",
            "#d70000",
        )
        self.bot.add_dashboard_log(
            "system",
            f"Rate limit protection: Bot paused for {pause_duration}s",
            "error",
        )

        self.bot.command_handler_status["rate_limited"] = True

        await self._trigger_idle_activities()

        await asyncio.sleep(pause_duration)

        self.bot.command_handler_status["rate_limited"] = False
        self._paused = False
        self._rate_limit_count = 0
        self._idle_triggered = False

        await self.bot.log(
            f"✅ Rate Limit Protection: Resuming after {pause_duration}s pause "
            f"(Total rate limits this session: {self._total_rate_limits})",
            "#51cf66",
        )
        self.bot.add_dashboard_log(
            "system",
            "Rate limit cooldown complete - bot resumed",
            "success",
        )

    async def _trigger_idle_activities(self):
        if self._idle_triggered:
            return
        self._idle_triggered = True

        await self.bot.log("💤 Hunt/Battle paused — running idle activities...", "#74c0fc")

        await asyncio.sleep(self.bot.random.uniform(1.5, 3.0))
        await self._trigger_rpp()

        await asyncio.sleep(self.bot.random.uniform(2.0, 4.0))
        await self._trigger_gems_scan()

    async def _trigger_rpp(self):
        try:
            rpp_cfg = self.bot.settings_dict.get("autoRandomCommands", {})
            if not rpp_cfg.get("enabled", False):
                return

            rpp_cog = self.bot.cogs.get("RPP")
            if rpp_cog:
                await rpp_cog.send_random_command()
                await self.bot.log("💤 Idle: Sent RPP command during rate-limit pause", "#74c0fc")
        except Exception as e:
            await self.bot.log(f"Error - idle RPP trigger: {e}", "#c25560")

    async def _trigger_gems_scan(self):
        try:
            gems_cfg = self.bot.settings_dict.get("autoUse", {}).get("gems", {})
            if not gems_cfg.get("enabled", False):
                return

            gems_cog = self.bot.cogs.get("Gems")
            if not gems_cog:
                return

            inv_cmd = {
                "cmd_name": self.bot.alias["inv"]["normal"],
                "prefix": True,
                "checks": True,
                "id": "inv",
            }
            gems_cog.inventory_check = True
            await self.bot.put_queue(inv_cmd, priority=True)
            await self.bot.log("💤 Idle: Scanning gems inventory during rate-limit pause", "#00d1d1")
        except Exception as e:
            await self.bot.log(f"Error - idle gems scan trigger: {e}", "#c25560")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.owo_bot_id:
            return

        rate_limit_phrases = [
            "slow down",
            "you're doing that too fast",
            "please wait",
            "calm down",
            "too many requests",
            "rate limit",
        ]

        content_lower = message.content.lower()
        if any(phrase in content_lower for phrase in rate_limit_phrases):
            if message.guild:
                is_for_me = (str(self.bot.user.id) in message.content) or any(
                    m.id == self.bot.user.id for m in message.mentions
                )
                if not is_for_me:
                    return

            self._rate_limit_count += 1
            self._last_rate_limit = time.time()
            self._total_rate_limits += 1

            await self.bot.log(
                f"⚡ OwO Rate Limit detected in message! "
                f"[{self._rate_limit_count}/{self._pause_threshold} in window]",
                "#ff6b6b",
            )

            if self._rate_limit_count >= self._pause_threshold and not self._paused:
                await self._auto_pause()


async def setup(bot):
    await bot.add_cog(RateLimitHandler(bot))