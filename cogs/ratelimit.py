"""
Mizu OwO Bot - Rate Limit Handler
Copyright (C) 2026 MizuNetwork
Copyright (C) 2026 Kiy0w0

Part of the OwOMizu Project (https://github.com/Kiy0w0/owomizu)
Handles Discord API rate limits by auto-pausing and resuming the bot.
"""

import asyncio
import time

from discord.ext import commands


class RateLimitHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._rate_limit_count = 0          # Consecutive rate limits
        self._last_rate_limit = 0           # Timestamp of last rate limit
        self._rate_limit_window = 60        # Window to count rate limits (seconds)
        self._pause_threshold = 3           # Pause after this many rate limits in window
        self._paused = False
        self._total_rate_limits = 0         # Lifetime counter

    @commands.Cog.listener()
    async def on_http_ratelimit(self, payload):
        """
        Fired when Discord sends a 429 rate limit response.
        payload attributes: retry_after, is_global, bucket, limit, remaining, reset_after
        """
        now = time.time()
        retry_after = getattr(payload, 'retry_after', 5.0)
        is_global = getattr(payload, 'is_global', False)
        
        self._total_rate_limits += 1
        
        # Reset counter if outside window
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

        # If too many rate limits in a short window, pause the bot
        if self._rate_limit_count >= self._pause_threshold and not self._paused:
            await self._auto_pause()

    async def _auto_pause(self):
        """Temporarily pause bot commands to cool down from rate limits."""
        self._paused = True
        
        # Calculate pause duration based on severity
        base_pause = 30  # Base pause: 30 seconds
        severity_multiplier = min(self._rate_limit_count, 10)  # Cap at 10x
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
        
        # Pause command handler
        self.bot.command_handler_status["rate_limited"] = True
        
        # Wait for cooldown
        await asyncio.sleep(pause_duration)
        
        # Resume
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
        """
        Detect OwO bot rate limit messages.
        OwO sometimes sends messages like "slow down" or "you're doing that too fast".
        """
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
