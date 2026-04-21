   

import asyncio
import json
import os
from discord.ext import commands

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._timed_pause_task = None

    def _save_settings(self):

        try:
            with open("config/settings.json", "w") as f:
                json.dump(self.bot.settings_dict, f, indent=4)
        except Exception as e:
            self.bot.loop.create_task(
                self.bot.log(f"[chat] Failed to save settings: {e}", "#c25560")
            )

    async def _toggle_command(self, cmd_key: str, enabled: bool, channel):
        node = self.bot.settings_dict.setdefault("commands", {}).setdefault(cmd_key, {})
        node["enabled"] = enabled
        self._save_settings()
        status = "enabled" if enabled else "disabled"
        await channel.send(
            f"{'▶️' if enabled else '⏹️'} **{cmd_key.title()}** {status}!",
            silent=True,
        )

    async def _toggle_nested(self, *keys, enabled: bool, channel):
        node = self.bot.settings_dict
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = enabled
        self._save_settings()
        label = ".".join(str(k) for k in keys)
        status = "enabled" if enabled else "disabled"
        await channel.send(
            f"{'▶️' if enabled else '⏹️'} **{label}** {status}!", silent=True
        )

    async def cog_load(self):
        cnf = self.bot.global_settings_dict.get('textCommands', {})
        p = cnf.get('prefix', '.')
        await self.bot.log(
            f"💬 Text Commands Ready! (prefix: '{p}')\n"
            f"  {p}help               → Show all commands\n"
            f"  {p}pause [mins]       → Pause farming (optional duration)\n"
            f"  {p}resume             → Resume farming\n"
            f"  {p}status             → Check bot status\n"
            f"  {p}restart            → Restart bot\n"
            f"  {p}stop               → Stop bot\n"
            f"  {p}cf <on|off>        → Toggle auto-coinflip\n"
            f"  {p}prey <on|off>      → Toggle auto-pray\n"
            f"  {p}curse <on|off>     → Toggle auto-curse\n"
            f"  {p}gems <on|off>      → Toggle gem auto-use\n"
            f"  {p}hunt <on|off>      → Toggle hunt\n"
            f"  {p}battle <on|off>    → Toggle battle",
            "#9dc3f5"
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        cnf = self.bot.global_settings_dict['textCommands']
        p = cnf['prefix']
        content = message.content.strip()
        content_lower = content.lower()

        is_allowed = message.author.id in [
            self.bot.user.id,
            1209017744696279041,
        ] + cnf["allowedUsers"]

        if f"{p}{cnf['commandToRestartAfterCaptcha']}" in content_lower:
            await self.bot.log("restarting Mizu after captcha", "#87875f")
            self.bot.add_dashboard_log(
                "system",
                f"Bot manually restarted after captcha by {message.author.name}",
                "info",
            )
            self.bot.command_handler_status["captcha"] = False
            await self.bot.log("Bot successfully restarted after captcha!", "#51cf66")
            return

        if not is_allowed:
            return

        ch = message.channel

        if f"{p}{cnf['commandToStopUser']}" in content_lower:
            await self.bot.log("stopping Mizu..", "#87875f")
            self.bot.should_exit = True
            await self.bot.close()
            import os; os._exit(0)

        elif f"{p}{cnf['commandToStartUser']}" in content_lower:
            await self.bot.log("starting Mizu..", "#87875f")
            self.bot.command_handler_status["sleep"] = False

        elif f"{p}help" in content_lower:
            await ch.send(
                f"**Mizu Commands** (prefix: `{p}`)\n"
                f"`{p}pause [mins]` — Pause farming (optionally resume after N minutes)\n"
                f"`{p}resume`       — Resume farming\n"
                f"`{p}status`       — Show current status & balance\n"
                f"`{p}restart`      — Restart bot process\n"
                f"`{p}stop`         — Permanently stop bot\n"
                f"`{p}cf  on|off`   — Toggle auto coinflip\n"
                f"`{p}pray on|off`  — Toggle auto pray\n"
                f"`{p}curse on|off` — Toggle auto curse\n"
                f"`{p}gems on|off`  — Toggle gem auto-use\n"
                f"`{p}hunt on|off`  — Toggle hunt command\n"
                f"`{p}battle on|off`— Toggle battle command",
                silent=True,
            )

        elif content_lower.startswith(f"{p}pause"):
            if self._timed_pause_task and not self._timed_pause_task.done():
                self._timed_pause_task.cancel()
                self._timed_pause_task = None

            parts = content.split()
            duration_mins = None
            if len(parts) >= 2:
                try:
                    duration_mins = float(parts[1])
                except ValueError:
                    pass

            await self.bot.log("Pausing Mizu...", "#e0aa3e")
            self.bot.command_handler_status["state"] = False
            self.bot.state_event.clear()
            self.bot.add_dashboard_log("system", "Bot paused by user command", "warning")

            if duration_mins:
                await ch.send(
                    f"⏸️ Bot paused for **{duration_mins}** minutes!", silent=True
                )
                async def _auto_resume():
                    await asyncio.sleep(duration_mins * 60)
                    if not self.bot.command_handler_status["state"]:
                        self.bot.command_handler_status["state"] = True
                        self.bot.state_event.set()
                        self.bot.add_dashboard_log(
                            "system", "Bot auto-resumed after timed pause", "success"
                        )
                        await self.bot.log("Auto-resumed after timed pause!", "#51cf66")
                        try:
                            await ch.send("▶️ Bot auto-resumed!", silent=True)
                        except Exception:
                            pass

                self._timed_pause_task = asyncio.create_task(_auto_resume())
            else:
                await ch.send("⏸️ Bot paused!", silent=True)

        elif f"{p}resume" in content_lower:
            if self._timed_pause_task and not self._timed_pause_task.done():
                self._timed_pause_task.cancel()
                self._timed_pause_task = None

            await self.bot.log("Resuming Mizu...", "#51cf66")
            self.bot.command_handler_status["state"] = True
            self.bot.state_event.set()
            self.bot.add_dashboard_log("system", "Bot resumed by user command", "success")
            await ch.send("▶️ Bot resumed!", silent=True)

        elif f"{p}status" in content_lower:
            is_paused = not self.bot.command_handler_status["state"]
            is_sleeping = self.bot.command_handler_status["sleep"]
            is_captcha = self.bot.command_handler_status["captcha"]
            bal = self.bot.user_status.get("balance", 0)
            earnings = self.bot.user_status.get("net_earnings", 0)
            state_str = (
                "⏸️ Paused" if is_paused
                else "😴 Sleeping" if is_sleeping
                else "🔒 Captcha" if is_captcha
                else "✅ Running"
            )
            cf_on  = self.bot.settings_dict.get("gamble", {}).get("coinflip", {}).get("enabled", False)
            pray_on = self.bot.settings_dict.get("commands", {}).get("pray", {}).get("enabled", False)
            curse_on = self.bot.settings_dict.get("commands", {}).get("curse", {}).get("enabled", False)
            gems_on = self.bot.settings_dict.get("autoUse", {}).get("gems", {}).get("enabled", False)
            await ch.send(
                f"**{self.bot.username} Status**\n"
                f"State: {state_str}\n"
                f"Balance: 🪙 {bal:,}  |  Earnings: 🪙 {earnings:,}\n"
                f"Coinflip: {'✅' if cf_on else '❌'}  |  Pray: {'✅' if pray_on else '❌'}  |  "
                f"Curse: {'✅' if curse_on else '❌'}  |  Gems: {'✅' if gems_on else '❌'}",
                silent=True,
            )

        elif f"{p}restart" in content_lower:
            await self.bot.log("Restarting Mizu...", "#e0aa3e")
            self.bot.add_dashboard_log("system", "Bot restarting by user command", "warning")
            await self.bot.close()
            import os, sys
            os.execl(sys.executable, sys.executable, *sys.argv)

        elif content_lower.startswith(f"{p}cf "):
            arg = content_lower.split(f"{p}cf ", 1)[1].strip()
            if arg in ("on", "off"):
                await self._toggle_nested("gamble", "coinflip", "enabled",
                                          enabled=(arg == "on"), channel=ch)
            else:
                await ch.send(f"Usage: `{p}cf on` or `{p}cf off`", silent=True)

        elif content_lower.startswith(f"{p}pray "):
            arg = content_lower.split(f"{p}pray ", 1)[1].strip()
            if arg in ("on", "off"):
                await self._toggle_command("pray", enabled=(arg == "on"), channel=ch)
            else:
                await ch.send(f"Usage: `{p}pray on` or `{p}pray off`", silent=True)

        elif content_lower.startswith(f"{p}curse "):
            arg = content_lower.split(f"{p}curse ", 1)[1].strip()
            if arg in ("on", "off"):
                await self._toggle_command("curse", enabled=(arg == "on"), channel=ch)
            else:
                await ch.send(f"Usage: `{p}curse on` or `{p}curse off`", silent=True)

        elif content_lower.startswith(f"{p}gems "):
            arg = content_lower.split(f"{p}gems ", 1)[1].strip()
            if arg in ("on", "off"):
                await self._toggle_nested("autoUse", "gems", "enabled",
                                          enabled=(arg == "on"), channel=ch)
            else:
                await ch.send(f"Usage: `{p}gems on` or `{p}gems off`", silent=True)

        elif content_lower.startswith(f"{p}hunt "):
            arg = content_lower.split(f"{p}hunt ", 1)[1].strip()
            if arg in ("on", "off"):
                await self._toggle_command("hunt", enabled=(arg == "on"), channel=ch)
            else:
                await ch.send(f"Usage: `{p}hunt on` or `{p}hunt off`", silent=True)

        elif content_lower.startswith(f"{p}battle "):
            arg = content_lower.split(f"{p}battle ", 1)[1].strip()
            if arg in ("on", "off"):
                await self._toggle_command("battle", enabled=(arg == "on"), channel=ch)
            else:
                await ch.send(f"Usage: `{p}battle on` or `{p}battle off`", silent=True)

async def setup(bot):
    await bot.add_cog(Chat(bot))