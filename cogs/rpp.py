import asyncio
import time
import random

from discord.ext import commands, tasks
from discord.ext.commands import ExtensionNotLoaded


class RPP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_command_time = 0
        self.commands_sent = 0
        
    async def cog_load(self):
        if not self.bot.settings_dict.get("autoRandomCommands", {}).get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.rpp"))
            except ExtensionNotLoaded:
                pass
        else:
            self.random_command_loop.start()
            await self.bot.log("RPP (Run/Pup/Piku) system loaded - commands will run every 1 minute randomly!", "#74c0fc")

    async def cog_unload(self):
        if hasattr(self, 'random_command_loop'):
            self.random_command_loop.cancel()
        await self.bot.remove_queue(id="rpp")
        await self.bot.log("RPP system unloaded.", "#74c0fc")

    async def should_send_command(self):
        """Check if we should send a random command based on conditions."""
        try:
            config = self.bot.settings_dict.get("autoRandomCommands", {})
            
            # Check if feature is enabled
            if not config.get("enabled", False):
                return False
            
            # Check if only when active and bot is not active
            if config.get("onlyWhenActive", True):
                if (self.bot.command_handler_status.get("captcha", False) or
                    self.bot.command_handler_status.get("sleep", False) or
                    not self.bot.command_handler_status.get("state", True)):
                    return False
                
            return True
            
        except Exception as e:
            await self.bot.log(f"Error in should_send_command: {e}", "#c25560")
            return False

    async def send_random_command(self):
        """Send a random command from the configured list."""
        try:
            # Always use run, pup, piku commands
            available_commands = ["run", "pup", "piku"]
            
            # Select random command
            selected_command = self.bot.random.choice(available_commands)
            
            # Create command object
            cmd = {
                "cmd_name": selected_command,
                "cmd_arguments": "",
                "prefix": True,
                "checks": False,
                "id": "rpp",
                "removed": False
            }
            
            # Send command
            await self.bot.put_queue(cmd, priority=False)
            
            # Update counters
            self.last_command_time = time.time()
            self.commands_sent += 1
            
            # Log the command
            await self.bot.log(f"RPP command sent: {selected_command} (Total sent: {self.commands_sent})", "#74c0fc")
            
            # Add dashboard log
            self.bot.add_dashboard_log("rpp", f"RPP command: {selected_command}", "info")
            
        except Exception as e:
            await self.bot.log(f"Error sending random command: {e}", "#c25560")
            self.bot.add_dashboard_log("rpp", f"Error sending RPP command: {e}", "error")

    @tasks.loop(seconds=60)  # Run every minute
    async def random_command_loop(self):
        """Main loop - sends a random RPP command every minute."""
        try:
            if await self.should_send_command():
                await self.send_random_command()
        except Exception as e:
            await self.bot.log(f"Error in random_command_loop: {e}", "#c25560")

    @random_command_loop.before_loop
    async def before_random_command_loop(self):
        """Wait for bot to be ready before starting loop."""
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for command responses (optional for future enhancements)."""
        if (message.channel.id == self.bot.cm.id and 
            message.author.id == self.bot.owo_bot_id):
            
            # Handle responses to random commands if needed
            # For now, just remove from queue when any OwO response is received
            # that might be related to our random commands
            content_lower = message.content.lower()
            
            if any(word in content_lower for word in [
                "you ran", "you pet", "you poke", 
                "running", "petting", "poking",
                "tired", "energy"
            ]):
                await self.bot.remove_queue(id="rpp")


async def setup(bot):
    await bot.add_cog(RPP(bot))
