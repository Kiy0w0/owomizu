"""
Mizu OwO Bot - Notification Helper Utility
Copyright (C) 2025 MizuNetwork

Centralized notification system for better logging and dashboard integration
"""

class NotificationHelper:
    """
    Helper class to standardize notifications across the bot.
    Makes notifications consistent and easier to manage.
    """
    
    # Notification types with their emojis
    TYPES = {
        "success": {"emoji": "✅", "color": "#51cf66"},
        "error": {"emoji": "❌", "color": "#c25560"},
        "warning": {"emoji": "⚠️", "color": "#ff9800"},
        "info": {"emoji": "ℹ️", "color": "#9dc3f5"},
        "captcha": {"emoji": "🔐", "color": "#e91e63"},
        "channel": {"emoji": "📍", "color": "#00bcd4"},
        "hunt": {"emoji": "🎯", "color": "#4caf50"},
        "battle": {"emoji": "⚔️", "color": "#f44336"},
        "daily": {"emoji": "🎁", "color": "#ff9800"},
        "cash": {"emoji": "💰", "color": "#ffd700"},
        "gems": {"emoji": "💎", "color": "#9c27b0"},
        "system": {"emoji": "🔧", "color": "#607d8b"},
    }
    
    @staticmethod
    def format_notification(message, notification_type="info"):
        """
        Format a notification with emoji and color.
        
        Args:
            message: The notification message
            notification_type: Type of notification (success, error, warning, info, etc.)
            
        Returns:
            tuple: (formatted_message, color_hex)
        """
        notif_config = NotificationHelper.TYPES.get(
            notification_type, 
            NotificationHelper.TYPES["info"]
        )
        
        emoji = notif_config["emoji"]
        color = notif_config["color"]
        
        # Add emoji to message if not already present
        if not any(e in message for e in ["✅", "❌", "⚠️", "ℹ️", "🔐", "📍", "🎯", "⚔️", "🎁", "💰", "💎", "🔧"]):
            formatted_message = f"{emoji} {message}"
        else:
            formatted_message = message
            
        return formatted_message, color
    
    @staticmethod
    async def send(bot, message, notification_type="info", dashboard=True, console=True):
        """
        Send a notification to console and/or dashboard.
        
        Args:
            bot: Bot instance
            message: Notification message
            notification_type: Type of notification
            dashboard: Send to dashboard logs (default: True)
            console: Send to console logs (default: True)
        """
        formatted_message, color = NotificationHelper.format_notification(message, notification_type)
        
        # Send to console
        if console and hasattr(bot, 'log'):
            await bot.log(formatted_message, color)
        
        # Send to dashboard
        if dashboard and hasattr(bot, 'add_dashboard_log'):
            bot.add_dashboard_log(notification_type, formatted_message, notification_type)
    
    @staticmethod
    def get_channel_switch_message(from_channel, to_channel, switch_count=None):
        """
        Generate a formatted channel switch message.
        
        Args:
            from_channel: Source channel name or ID
            to_channel: Destination channel name or ID  
            switch_count: Optional switch counter
            
        Returns:
            str: Formatted message
        """
        if switch_count is not None:
            return f"Switched from '{from_channel}' to '{to_channel}' (#{switch_count})"
        else:
            return f"Switched from '{from_channel}' to '{to_channel}'"
    
    @staticmethod
    def get_error_message(component, error, truncate=50):
        """
        Generate a formatted error message.
        
        Args:
            component: Component name (e.g., "Channel Switcher", "Hunt")
            error: Error object or string
            truncate: Max length of error message
            
        Returns:
            str: Formatted error message
        """
        error_str = str(error)
        if len(error_str) > truncate:
            error_str = error_str[:truncate] + "..."
        return f"{component} error: {error_str}"


# Example usage in other files:
# from utils.notifications import NotificationHelper
#
# # Simple notification
# await NotificationHelper.send(self.bot, "Channel switched successfully", "success")
#
# # Channel switch notification
# message = NotificationHelper.get_channel_switch_message("channel-1", "channel-2", 5)
# await NotificationHelper.send(self.bot, message, "channel")
#
# # Error notification
# message = NotificationHelper.get_error_message("Hunt", exception_object)
# await NotificationHelper.send(self.bot, message, "error")
