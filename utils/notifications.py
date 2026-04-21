   

class NotificationHelper:

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

        notif_config = NotificationHelper.TYPES.get(
            notification_type, 
            NotificationHelper.TYPES["info"]
        )

        emoji = notif_config["emoji"]
        color = notif_config["color"]

        if not any(e in message for e in ["✅", "❌", "⚠️", "ℹ️", "🔐", "📍", "🎯", "⚔️", "🎁", "💰", "💎", "🔧"]):
            formatted_message = f"{emoji} {message}"
        else:
            formatted_message = message

        return formatted_message, color

    @staticmethod
    async def send(bot, message, notification_type="info", dashboard=True, console=True):

        formatted_message, color = NotificationHelper.format_notification(message, notification_type)

        if console and hasattr(bot, 'log'):
            await bot.log(formatted_message, color)

        if dashboard and hasattr(bot, 'add_dashboard_log'):
            bot.add_dashboard_log(notification_type, formatted_message, notification_type)

    @staticmethod
    def get_channel_switch_message(from_channel, to_channel, switch_count=None):

        if switch_count is not None:
            return f"Switched from '{from_channel}' to '{to_channel}' (#{switch_count})"
        else:
            return f"Switched from '{from_channel}' to '{to_channel}'"

    @staticmethod
    def get_error_message(component, error, truncate=50):

        error_str = str(error)
        if len(error_str) > truncate:
            error_str = error_str[:truncate] + "..."
        return f"{component} error: {error_str}"

