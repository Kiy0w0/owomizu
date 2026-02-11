import asyncio
import time
from discord.ext import commands

class Safety(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.is_safety_paused = False
        
        # Default config (fallback if not in settings)
        self.default_run_minutes = 120 # Run for 2 hours
        self.default_pause_minutes = 15 # Sleep for 15 mins

    async def cog_load(self):
        # We check configs
        if not self.bot.settings_dict.get("safety", {}).get("enabled", False):
            await self.bot.log("Safety System disabled (enable in settings for anti-ban)", "#9dc3f5")
        else:
            await self.bot.log("Safety System Loaded 🛡️", "#51cf66")
            self.bot.loop.create_task(self.safety_loop())

    async def safety_loop(self):
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                # Get Configs
                safety_conf = self.bot.settings_dict.get("safety", {})
                if not safety_conf.get("enabled", False):
                    await asyncio.sleep(60)
                    continue
                    
                run_duration = safety_conf.get("runTimeMinutes", self.default_run_minutes) * 60
                pause_duration = safety_conf.get("sleepTimeMinutes", self.default_pause_minutes) * 60
                
                # Check uptime
                uptime = time.time() - self.start_time
                
                if uptime >= run_duration:
                    # Time to sleep!
                    self.is_safety_paused = True
                    self.bot.command_handler_status["sleep"] = True
                    
                    await self.bot.log(f"🛡️ Safety Pause: Sleeping for {int(pause_duration/60)} minutes...", "#e67e22")
                    self.bot.add_dashboard_log("system", "Starting Safety Sleep", "warning")
                    
                    # Sleep period
                    await asyncio.sleep(pause_duration)
                    
                    # Wake up
                    self.start_time = time.time() # Reset timer
                    self.is_safety_paused = False
                    self.bot.command_handler_status["sleep"] = False
                    
                    await self.bot.log("🛡️ Safety Pause: Resuming farming!", "#2ecc71")
                    self.bot.add_dashboard_log("system", "Resumed from Safety Sleep", "success")
                
                await asyncio.sleep(60) # Check every minute

            except Exception as e:
                await self.bot.log(f"Safety Loop Error: {e}", "#c25560")
                await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Check for Auto-Stop Triggers"""
        # Checks if safety or autoStop enabled
        safety_conf = self.bot.settings_dict.get("safety", {})
        if not safety_conf.get("enabled", False):
           return
        
        auto_stop_conf = safety_conf.get("autoStop", {})
        if not auto_stop_conf.get("enabled", False):
            return

        # Check only in monitored channels (optional, but safer)
        # If trigger is global (e.g. DM form bot), remove channel check
        if message.channel.id not in self.bot.list_channel and not isinstance(message.channel, int): 
            # We assume message.channel is an object, list_channel has IDs.
            # But let's be safe and check all incoming messages for now creates less risk.
            pass

        content_lower = message.content.lower()
        triggers = [t.lower() for t in auto_stop_conf.get("triggers", [])]
        
        for trigger in triggers:
            if trigger in content_lower:
                # MATCH FOUND!
                await self.bot.log(f"🛑 AUTO-STOP TRIGGERED: '{trigger}' detected in message!", "#e74c3c")
                self.bot.command_handler_status["state"] = False # STOP THE BOT
                self.bot.add_dashboard_log("system", f"Auto-Stop Triggered: {trigger}", "critical")
                
                # Optional: Send alert to webhook if configured (skipped for now)
                await self.bot.log("Bot has been PAUSED indefinitely due to safety trigger.", "#e74c3c")
                break

async def setup(bot):
    await bot.add_cog(Safety(bot))
