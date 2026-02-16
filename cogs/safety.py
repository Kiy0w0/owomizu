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
                    
                # 1. Check Working Hours (Human Sleep Schedule)
                # Default: Active 24/7 if not configured
                work_schedule = safety_conf.get("workSchedule", {"enabled": False})
                if work_schedule.get("enabled", False):
                    import datetime
                    now = datetime.datetime.now()
                    current_hour = now.hour
                    
                    start_hour = work_schedule.get("startHour", 7) # 7 AM
                    end_hour = work_schedule.get("endHour", 23)   # 11 PM
                    
                    # Logic: If current hour is NOT in range, sleep!
                    # Handle case where end_hour < start_hour (night shift)
                    is_working_time = False
                    if start_hour <= end_hour:
                         is_working_time = start_hour <= current_hour < end_hour
                    else:
                         is_working_time = current_hour >= start_hour or current_hour < end_hour
                    
                    if not is_working_time:
                         if not self.bot.command_handler_status["sleep"]:
                             await self.bot.log(f"Security Schedule: It's late! Sleeping until {start_hour}:00...", "#95a5a6")
                             self.bot.command_handler_status["sleep"] = True
                             self.bot.add_dashboard_log("system", "Sleeping (Schedule)", "warning")
                         await asyncio.sleep(60)
                         continue
                    else:
                         # Wake up if we were sleeping due to schedule
                         # But be careful not to wake up if we are in 'Safety Pause' mode
                         if self.bot.command_handler_status["sleep"] and not self.is_safety_paused:
                              await self.bot.log(f"Security Schedule: Farming...", "#f1c40f")
                              self.bot.command_handler_status["sleep"] = False
                              self.start_time = time.time() # Reset run timer

                # 2. Safety Pause Logic
                run_duration = safety_conf.get("runTimeMinutes", self.default_run_minutes) * 60
                
                # Check uptime
                if (time.time() - self.start_time) >= run_duration:
                    # Time to sleep!
                    self.is_safety_paused = True
                    self.bot.command_handler_status["sleep"] = True
                    
                    # Randomize Sleep Duration (+/- 20%)
                    base_sleep = safety_conf.get("sleepTimeMinutes", self.default_pause_minutes) * 60
                    variance = base_sleep * 0.2
                    actual_sleep = base_sleep + self.bot.random.uniform(-variance, variance)
                    
                    await self.bot.log(f"🛡️ Safety Pause: Taking a break for {int(actual_sleep/60)} minutes...", "#e67e22")
                    self.bot.add_dashboard_log("system", "Starting Safety Sleep", "warning")
                    
                    # Sleep period
                    await asyncio.sleep(actual_sleep)
                    
                    # Wake up
                    self.start_time = time.time() # Reset timer
                    self.is_safety_paused = False
                    self.bot.command_handler_status["sleep"] = False
                    
                    await self.bot.log("🛡️ Safety Pause: Resumed farming!", "#2ecc71")
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

        # Check only in monitored channels, but allow DMs (where guild is None)
        if message.guild and message.channel.id not in self.bot.list_channel:
            return

        content_lower = message.content.lower()
        
        # 1. Check Delay Triggers (Temporary Stop)
        delay_triggers = [t.lower() for t in auto_stop_conf.get("delayTriggers", [])]
        for trigger in delay_triggers:
            if trigger in content_lower:
                # MATCH FOUND!
                delay_duration = auto_stop_conf.get("delayDuration", 300)
                await self.bot.log(f"⚠️ Cooldown Triggered: '{trigger}' detected! Sleeping for {delay_duration} seconds...", "#f39c12")
                self.bot.add_dashboard_log("system", f"Temporary Pause (Cooldown): {trigger}", "warning")
                
                # Start temporary sleep task
                # We use create_task so it doesn't block the listener
                self.bot.loop.create_task(self.temporary_sleep(delay_duration))
                return

        # 2. Check Auto-Stop Triggers (Permanent Stop)
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
    
    async def temporary_sleep(self, duration):
        """Helper to sleep for a duration then wake up"""
        if self.bot.command_handler_status["sleep"]:
            return # Already sleeping
            
        self.bot.command_handler_status["sleep"] = True
        await asyncio.sleep(duration)
        
        # BEFORE WAKING UP: Check if we are in 'Human Schedule' sleep time?
        safety_conf = self.bot.settings_dict.get("safety", {})
        work_schedule = safety_conf.get("workSchedule", {"enabled": False})
        
        if work_schedule.get("enabled", False):
            import datetime
            now = datetime.datetime.now()
            current_hour = now.hour
            
            start = work_schedule.get("startHour", 7)
            end = work_schedule.get("endHour", 23)
            
            is_working_time = False
            if start <= end:
                 is_working_time = start <= current_hour < end
            else:
                 is_working_time = current_hour >= start or current_hour < end
            
            if not is_working_time:
                 # It is sleeping time! Do not wake up.
                 # The main safety_loop will handle waking up when morning comes.
                 await self.bot.log("🕒 Cooldown expired, but it's sleeptime. Staying asleep.", "#95a5a6")
                 return

        self.bot.command_handler_status["sleep"] = False
        await self.bot.log("✅ Cooldown expired. Resuming bot activity!", "#2ecc71")

async def setup(bot):
    await bot.add_cog(Safety(bot))
