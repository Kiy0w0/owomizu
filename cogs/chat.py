"""
Mizu OwO Bot
Copyright (C) 2025 MizuNetwork
Copyright (C) 2025 Kiy0w0
"""

from discord.ext import commands
import os
import sys


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        cnf = self.bot.global_settings_dict.get('textCommands', {})
        p = cnf.get('prefix', '.')
        await self.bot.log(
            f"💬 Text Commands Ready! Use in DM or farming channel:\n"
            f"  {p}pause       → Pause farming\n"
            f"  {p}resume      → Resume farming\n"
            f"  {p}status      → Check bot status\n"
            f"  {p}restart     → Restart bot\n"
            f"  {p}stop        → Stop bot",
            "#9dc3f5"
        )

    @commands.Cog.listener()
    async def on_message(self, message):

        cnf = self.bot.global_settings_dict['textCommands']

        if message.author.id in [self.bot.user.id, 1209017744696279041] + cnf["allowedUsers"]:
            if f"{cnf['prefix']}{cnf['commandToStopUser']}" in message.content.lower():
                await self.bot.log("stopping Mizu..","#87875f")
                self.bot.should_exit = True
                await self.bot.close()
                import os; os._exit(0)

            elif f"{cnf['prefix']}{cnf['commandToStartUser']}" in message.content.lower():
                await self.bot.log("starting Mizu..","#87875f")
                self.bot.command_handler_status["sleep"] = False

            elif f"{cnf['prefix']}pause" in message.content.lower():
                await self.bot.log("⏸️ Pausing Mizu...", "#e0aa3e")
                self.bot.command_handler_status["state"] = False
                self.bot.state_event.clear()
                self.bot.add_dashboard_log("system", "Bot paused by user command", "warning")
                await message.channel.send("⏸️ Bot paused!", silent=True)

            elif f"{cnf['prefix']}resume" in message.content.lower():
                await self.bot.log("▶️ Resuming Mizu...", "#51cf66")
                self.bot.command_handler_status["state"] = True
                self.bot.state_event.set()
                self.bot.add_dashboard_log("system", "Bot resumed by user command", "success")
                await message.channel.send("▶️ Bot resumed!", silent=True)

            elif f"{cnf['prefix']}status" in message.content.lower():
                is_paused = not self.bot.command_handler_status["state"]
                is_sleeping = self.bot.command_handler_status["sleep"]
                is_captcha = self.bot.command_handler_status["captcha"]
                bal = self.bot.user_status.get('balance', 0)
                earnings = self.bot.user_status.get('net_earnings', 0)
                state_str = "⏸️ Paused" if is_paused else ("😴 Sleeping" if is_sleeping else ("🔒 Captcha" if is_captcha else "✅ Running"))
                await message.channel.send(
                    f"**{self.bot.username} Status**\n"
                    f"State: {state_str}\n"
                    f"Balance: 🪙 {bal:,}  |  Earnings: 🪙 {earnings:,}",
                    silent=True
                )

            elif f"{cnf['prefix']}restart" in message.content.lower():
                await self.bot.log("Restarting Mizu...", "#e0aa3e")
                self.bot.add_dashboard_log("system", "Bot restarting by user command", "warning")
                await self.bot.close()
                import os, sys
                os.execl(sys.executable, sys.executable, *sys.argv)

        if f"{cnf['prefix']}{cnf['commandToRestartAfterCaptcha']}" in message.content.lower():
            await self.bot.log("restarting Mizu after captcha","#87875f")
            
            # Add dashboard log for manual captcha restart
            self.bot.add_dashboard_log("system", f"Bot manually restarted after captcha by {message.author.name}", "info")
            
            self.bot.command_handler_status["captcha"]=False
            
            await self.bot.log("Bot successfully restarted after captcha!", "#51cf66")

async def setup(bot):
    await bot.add_cog(Chat(bot))