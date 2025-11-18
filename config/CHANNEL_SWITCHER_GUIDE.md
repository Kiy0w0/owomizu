# Channel Switcher Configuration Guide

## What is Channel Switcher?
The Channel Switcher automatically rotates your farm bot between different Discord channels to avoid detection and distribute activity.

## How to Configure

### Easy Setup (in `config/settings.json`)

```json
"channelSwitcher": {
    "enabled": true,
    "users": [
        {
            "userid": YOUR_DISCORD_USER_ID,
            "channels": [
                CHANNEL_ID_1,
                CHANNEL_ID_2,
                CHANNEL_ID_3
            ]
        }
    ],
    "interval": [300, 600],
    "delayBeforeSwitch": [2, 4]
}
```

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean | Turn channel switching on/off |
| `userid` | number | Your Discord user ID |
| `channels` | array | List of channel IDs to rotate between |
| `interval` | array [min, max] | How often to switch channels (in seconds) |
| `delayBeforeSwitch` | array [min, max] | Delay before actually switching (in seconds) |

### How to Get Channel IDs

1. Enable Discord Developer Mode:
   - Settings → Advanced → Developer Mode → ON
2. Right-click any channel → Copy ID

### Example Configuration

```json
"channelSwitcher": {
    "enabled": true,
    "users": [
        {
            "userid": 123456789012345678,
            "channels": [
                987654321098765432,
                876543210987654321,
                765432109876543210
            ]
        },
        {
            "userid": 234567890123456789,
            "channels": [
                654321098765432109,
                543210987654321098
            ]
        }
    ],
    "interval": [300, 600],
    "delayBeforeSwitch": [2, 4]
}
```

This means:
- The bot will switch channels every 5-10 minutes (300-600 seconds)
- Will wait 2-4 seconds before actually switching
- User 1 will rotate between 3 channels
- User 2 will rotate between 2 channels

### Tips

- **Minimum 2 channels**: You need at least 2 channels for rotation
- **Same server**: All channels must be in the same Discord server
- **Bot access**: Make sure the bot has access to all channels
- **Don't spam**: Set realistic intervals (5+ minutes recommended)

## Notifications

When Channel Switcher is active, you'll see:
- ✅ Success messages when switching channels
- ⚠️ Warning messages if a channel is busy
- ❌ Error messages if switching fails

All notifications appear in:
- Console logs
- Web dashboard
- Discord logs (if configured)
