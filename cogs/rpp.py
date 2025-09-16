import asyncio
import time
import random

from discord.ext import commands, tasks
from discord.ext.commands import ExtensionNotLoaded


class RPP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_command_time = 0
        self.commands_this_hour = 0
        self.hour_reset_time = time.time() + 3600  # Reset counter every hour
        self.next_command_time = 0
        
    async def cog_load(self):
        if not self.bot.settings_dict.get("autoRandomCommands", {}).get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.rpp"))
            except ExtensionNotLoaded:
                pass
        else:
            # Schedule first random command
            await self.schedule_next_command()
            # Start the loop
            self.random_command_loop.start()

    async def cog_unload(self):
        if hasattr(self, 'random_command_loop'):
            self.random_command_loop.cancel()
        await self.bot.remove_queue(id="rpp")

    def get_random_interval(self):
        """Get random interval in seconds based on settings."""
        config = self.bot.settings_dict.get("autoRandomCommands", {})
        interval_minutes = config.get("intervalMinutes", [30, 120])
        min_minutes, max_minutes = interval_minutes
        return self.bot.random.uniform(min_minutes * 60, max_minutes * 60)

    async def schedule_next_command(self):
        """Schedule the next random command."""
        interval = self.get_random_interval()
        self.next_command_time = time.time() + interval
        await self.bot.log(f"Next random command scheduled in {interval/60:.1f} minutes", "#74c0fc")

    def should_send_command(self):
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
            
            # Reset hourly counter if needed
            current_time = time.time()
            if current_time > self.hour_reset_time:
                self.commands_this_hour = 0
                self.hour_reset_time = current_time + 3600
            
            # Check max commands per hour
            max_per_hour = config.get("maxCommandsPerHour", 8)
            if self.commands_this_hour >= max_per_hour:
                return False
            
            # Check if it's time for next command
            if current_time < self.next_command_time:
                return False
                
            return True
            
        except Exception as e:
            asyncio.create_task(self.bot.log(f"Error in should_send_command: {e}", "#c25560"))
            return False

    async def send_random_command(self):
        """Send a random command from the configured list."""
        try:
            config = self.bot.settings_dict.get("autoRandomCommands", {})
            available_commands = config.get("commands", ["run", "pup", "piku"])
            
            if not available_commands:
                await self.bot.log("No random commands configured", "#ff6b6b")
                return
            
            # Select random command
            if config.get("randomizeOrder", True):
                selected_command = self.bot.random.choice(available_commands)
            else:
                # Use round-robin if not randomizing
                index = self.commands_this_hour % len(available_commands)
                selected_command = available_commands[index]
            
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
            self.commands_this_hour += 1
            
            # Log the command
            await self.bot.log(f"Random command sent: {selected_command} ({self.commands_this_hour}/{config.get('maxCommandsPerHour', 8)} this hour)", "#74c0fc")
            
            # Add dashboard log
            self.bot.add_dashboard_log("rpp", f"RPP command: {selected_command}", "info")
            
            # Schedule next command
            await self.schedule_next_command()
            
        except Exception as e:
            await self.bot.log(f"Error sending random command: {e}", "#c25560")

    @tasks.loop(seconds=60)  # Check every minute
    async def random_command_loop(self):
        """Main loop for random command scheduling."""
        try:
            if self.should_send_command():
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
