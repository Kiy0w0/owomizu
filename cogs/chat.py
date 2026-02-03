"""
Mizu OwO Bot
Copyright (C) 2025 MizuNetwork
Copyright (C) 2025 Kiy0w0
"""

from discord.ext import commands


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):

        cnf = self.bot.global_settings_dict['textCommands']

        if message.author.id in [self.bot.user.id, 1209017744696279041] + cnf["allowedUsers"]:
            if f"{cnf['prefix']}{cnf['commandToStopUser']}" in message.content.lower():
                await self.bot.log("stopping Mizu..","#87875f")
                self.bot.should_exit = True
                await self.bot.close()

            elif f"{cnf['prefix']}{cnf['commandToStartUser']}" in message.content.lower():
                await self.bot.log("starting Mizu..","#87875f")
                self.bot.command_handler_status["sleep"]=False

            elif f"{cnf['prefix']}pause" in message.content.lower():
                await self.bot.log("Pausing Mizu...", "#e0aa3e")
                await self.bot.set_stat(False, "user_pause")
                self.bot.add_dashboard_log("system", "Bot paused by user command", "warning")

            elif f"{cnf['prefix']}resume" in message.content.lower():
                await self.bot.log("Resuming Mizu...", "#51cf66")
                await self.bot.set_stat(True, "user_resume")
                self.bot.add_dashboard_log("system", "Bot resumed by user command", "success")

        if f"{cnf['prefix']}{cnf['commandToRestartAfterCaptcha']}" in message.content.lower():
            await self.bot.log("restarting Mizu after captcha","#87875f")
            
            # Add dashboard log for manual captcha restart
            self.bot.add_dashboard_log("system", f"Bot manually restarted after captcha by {message.author.name}", "info")
            
            self.bot.command_handler_status["captcha"]=False
            
            await self.bot.log("Bot successfully restarted after captcha!", "#51cf66")

async def setup(bot):
    await bot.add_cog(Chat(bot))