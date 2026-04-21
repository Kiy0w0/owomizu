   

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

    @commands.Cog.listener()
    async def on_http_ratelimit(self, payload):

        now = time.time()
        retry_after = getattr(payload, 'retry_after', 5.0)
        is_global = getattr(payload, 'is_global', False)

        self._total_rate_limits += 1

        if now - self._last_rate_limit > self._rate_limit_window:
            self._rate_limit_count = 0

        self._rate_limit_count += 1
        self._last_rate_limit = now

        scope = "🌐 GLOBAL" if is_global else "📦 Bucket"
        await self.bot.log(
            f"⚡ Rate Limited! ({scope}) - Retry after {retry_after:.1f}s "
            f"[{self._rate_limit_count}/{self._pause_threshold} in window]",
            "#ff6b6b"
        )
        self.bot.add_dashboard_log(
            "system",
            f"Rate limit hit ({self._rate_limit_count}x) - retry after {retry_after:.1f}s",
            "warning"
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
            "#d70000"
        )
        self.bot.add_dashboard_log(
            "system",
            f"Rate limit protection: Bot paused for {pause_duration}s",
            "error"
        )

        self.bot.command_handler_status["rate_limited"] = True

        await asyncio.sleep(pause_duration)

        self.bot.command_handler_status["rate_limited"] = False
        self._paused = False
        self._rate_limit_count = 0

        await self.bot.log(
            f"✅ Rate Limit Protection: Resuming after {pause_duration}s pause "
            f"(Total rate limits this session: {self._total_rate_limits})",
            "#51cf66"
        )
        self.bot.add_dashboard_log(
            "system",
            "Rate limit cooldown complete - bot resumed",
            "success"
        )

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
                is_for_me = (str(self.bot.user.id) in message.content) or any(m.id == self.bot.user.id for m in message.mentions)
                if not is_for_me:
                    return

            self._rate_limit_count += 1
            self._last_rate_limit = time.time()
            self._total_rate_limits += 1

            await self.bot.log(
                f"⚡ OwO Rate Limit detected in message! "
                f"[{self._rate_limit_count}/{self._pause_threshold} in window]",
                "#ff6b6b"
            )

            if self._rate_limit_count >= self._pause_threshold and not self._paused:
                await self._auto_pause()

async def setup(bot):
    await bot.add_cog(RateLimitHandler(bot))