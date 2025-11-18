"""
Mizu OwO Bot - Channel Switcher
Copyright (C) 2025 MizuNetwork
Copyright (C) 2025 Kiy0w0

Automatically switches between configured channels for farming automation
"""

import asyncio
from discord.ext import commands, tasks
from datetime import datetime, timezone
from discord.ext.commands import ExtensionNotLoaded


class ChannelSwitcher(commands.Cog):
    """
    Automatically switches farming channels based on interval settings.
    Easier configuration - just edit the 'channelSwitcher' section in settings.json
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.last_switch_time = None
        self.switch_count = 0

    @tasks.loop()
    async def switch_channel_loop(self):
        """Main loop that triggers channel switches at configured intervals"""
        await self.bot.sleep_till(self.bot.settings_dict["channelSwitcher"]["interval"])
        
        success, message = await self.change_channel()

        if success:
            # Success notification
            await self.bot.log(f"✅ Channel Switcher: {message}", "#51cf66")
            self.bot.add_dashboard_log("system", f"📍 {message}", "success")
        else:
            # Error notification
            await self.bot.log(f"❌ Channel Switcher Error: {message}", "#c25560")
            self.bot.add_dashboard_log("system", f"⚠️ {message}", "error")

    async def change_channel(self):
        """
        Change to a different channel from the configured list.
        Returns: (success: bool, message: str)
        """
        try:
            config = self.bot.settings_dict["channelSwitcher"]
            current_channel_id = self.bot.cm.id
            current_channel_name = self.bot.cm.name
            
            # Find user's channel configuration
            user_config = self._get_user_config(config)
            if not user_config:
                return False, f"No channel configuration found for user {self.bot.user.id}"
            
            # Get available channels (exclude current channel)
            available_channels = [
                cid for cid in user_config["channels"] 
                if cid != current_channel_id
            ]
            
            if not available_channels:
                return False, f"No alternative channels configured (currently in: {current_channel_name})"
            
            # Try switching to each channel until successful
            attempted_channels = []
            for channel_id in self.bot.random.sample(available_channels, len(available_channels)):
                attempted_channels.append(channel_id)
                
                try:
                    new_channel = await self.bot.fetch_channel(channel_id)
                    if not new_channel:
                        await self.bot.log(f"⚠️ Channel ID {channel_id} not found", "#ff9800")
                        continue
                    
                    # Check if channel is safe to switch to (no recent activity)
                    if not await self._is_channel_safe(new_channel):
                        await self.bot.log(f"⏳ Channel '{new_channel.name}' has recent activity, skipping", "#9dc3f5")
                        continue
                    
                    # Perform the switch
                    await self.bot.empty_checks_and_switch(new_channel)
                    
                    # Update statistics
                    self.switch_count += 1
                    self.last_switch_time = datetime.now(timezone.utc)
                    
                    return True, f"Switched from '{current_channel_name}' to '{new_channel.name}' (#{self.switch_count})"
                    
                except Exception as e:
                    await self.bot.log(f"⚠️ Error accessing channel {channel_id}: {str(e)[:50]}", "#ff6b6b")
                    continue
            
            # All channels failed
            return False, f"Could not switch channels - tried {len(attempted_channels)} channels, all failed"
            
        except Exception as e:
            return False, f"Unexpected error in channel switcher: {str(e)}"

    def _get_user_config(self, config):
        """
        Helper: Find channel configuration for current user.
        Makes it easy to see what the config structure should be.
        """
        for user_entry in config.get("users", []):
            if user_entry.get("userid") == self.bot.user.id:
                return user_entry
        return None

    async def _is_channel_safe(self, channel):
        """
        Helper: Check if channel is safe to switch to (no recent activity).
        Returns True if no messages in last 5 seconds, False otherwise.
        """
        try:
            async for message in channel.history(limit=1):
                current_time = datetime.now(timezone.utc)
                time_since_last_msg = (current_time - message.created_at).total_seconds()
                return time_since_last_msg > 5
            # No messages in channel history
            return True
        except Exception:
            # If we can't check, assume it's safe
            return True

    async def cog_load(self):
        """Called when cog is loaded - starts the channel switcher loop"""
        if not self.bot.settings_dict["channelSwitcher"]["enabled"]:
            try:
                await self.bot.log("ℹ️ Channel Switcher is disabled in settings", "#9dc3f5")
                asyncio.create_task(self.bot.unload_cog("cogs.channelSwitcher"))
            except ExtensionNotLoaded:
                pass
        else:
            await self.bot.log("🔄 Channel Switcher activated", "#51cf66")
            self.bot.add_dashboard_log("system", "🔄 Channel Switcher started", "info")
            self.switch_channel_loop.start()

    async def cog_unload(self):
        """Called when cog is unloaded - stops the channel switcher loop"""
        self.switch_channel_loop.cancel()
        await self.bot.log("🛑 Channel Switcher deactivated", "#9dc3f5")
        self.bot.add_dashboard_log("system", "🛑 Channel Switcher stopped", "info")


async def setup(bot):
    """Setup function to add this cog to the bot"""
    await bot.add_cog(ChannelSwitcher(bot))
