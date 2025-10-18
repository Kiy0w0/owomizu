import aiohttp
import asyncio
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any

class DiscordWebhook:
    """Discord Webhook Integration for OwOMizu Bot"""
    
    def __init__(self, webhook_url: str, username: str = "Mizu OwO Bot", avatar_url: str = None):
        self.webhook_url = webhook_url
        self.username = username
        self.avatar_url = avatar_url or "https://cdn.discordapp.com/attachments/1234567890/mizu_logo.png"
        self.session = None
        
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    def create_embed(
        self,
        title: str,
        description: str = None,
        color: int = 0x00D7AF,
        fields: list = None,
        footer: str = None,
        thumbnail: str = None,
        image: str = None,
        timestamp: bool = True
    ) -> Dict[str, Any]:
        """Create a Discord embed"""
        embed = {
            "title": title,
            "color": color
        }
        
        if description:
            embed["description"] = description
            
        if fields:
            embed["fields"] = fields
            
        if footer:
            embed["footer"] = {"text": footer}
            
        if thumbnail:
            embed["thumbnail"] = {"url": thumbnail}
            
        if image:
            embed["image"] = {"url": image}
            
        if timestamp:
            embed["timestamp"] = datetime.now(timezone.utc).isoformat()
            
        return embed
        
    async def send(
        self,
        content: str = None,
        embeds: list = None,
        username: str = None,
        avatar_url: str = None
    ) -> bool:
        """Send webhook message"""
        try:
            session = await self.get_session()
            
            payload = {
                "username": username or self.username,
                "avatar_url": avatar_url or self.avatar_url
            }
            
            if content:
                payload["content"] = content
                
            if embeds:
                payload["embeds"] = embeds
                
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status in [200, 204]:
                    return True
                else:
                    print(f"Webhook failed: {response.status} - {await response.text()}")
                    return False
                    
        except Exception as e:
            print(f"Webhook error: {e}")
            return False
            
    async def send_captcha_alert(
        self,
        account_name: str,
        channel_name: str,
        captcha_type: str,
        screenshot_url: str = None,
        user_id_to_ping: str = None
    ):
        """Send captcha alert with screenshot"""
        embed = self.create_embed(
            title="🚨 CAPTCHA DETECTED",
            description=f"**Account:** {account_name}\n**Channel:** {channel_name}\n**Type:** {captcha_type}",
            color=0xFF0000,  # Red
            image=screenshot_url,
            footer="Solve this captcha immediately!"
        )
        
        content = f"<@{user_id_to_ping}> **CAPTCHA ALERT!**" if user_id_to_ping else None
        
        await self.send(content=content, embeds=[embed])
        
    async def send_ban_alert(
        self,
        account_name: str,
        reason: str = "Unknown",
        user_id_to_ping: str = None
    ):
        """Send ban/warning alert"""
        embed = self.create_embed(
            title="⛔ ACCOUNT BANNED",
            description=f"**Account:** {account_name}\n**Reason:** {reason}\n\n**Action Required:** Check your account immediately!",
            color=0xFF0000,  # Red
            thumbnail="https://cdn.discordapp.com/emojis/ban_emoji.png",
            footer="Account action detected by Mizu OwO Bot"
        )
        
        content = f"<@{user_id_to_ping}> **⚠️ URGENT: ACCOUNT BANNED!**" if user_id_to_ping else None
        
        await self.send(content=content, embeds=[embed])
        
    async def send_rare_catch(
        self,
        account_name: str,
        rarity: str,
        animal_name: str,
        animal_emoji: str = None
    ):
        """Send rare animal catch notification"""
        colors = {
            "mythical": 0xFF00FF,  # Magenta
            "fabled": 0xFFD700,    # Gold
            "legendary": 0xFFA500   # Orange
        }
        
        emojis = {
            "mythical": "✨",
            "fabled": "🌟",
            "legendary": "⭐"
        }
        
        emoji = emojis.get(rarity.lower(), "🎉")
        color = colors.get(rarity.lower(), 0xFFD43B)
        
        embed = self.create_embed(
            title=f"{emoji} {rarity.upper()} CATCH!",
            description=f"**Account:** {account_name}\n**Animal:** {animal_emoji or ''} {animal_name}\n\nCongratulations on this rare catch!",
            color=color,
            footer=f"Rare animal caught by Mizu OwO Bot"
        )
        
        await self.send(embeds=[embed])
        
    async def send_daily_summary(
        self,
        account_name: str,
        stats: Dict[str, Any]
    ):
        """Send daily summary report"""
        fields = []
        
        # Commands executed
        if "commands" in stats:
            cmd_text = "\n".join([f"• {cmd}: {count}" for cmd, count in stats["commands"].items()])
            fields.append({
                "name": "📊 Commands Executed",
                "value": cmd_text or "No commands",
                "inline": False
            })
        
        # Earnings
        if "earnings" in stats:
            fields.append({
                "name": "💰 Earnings",
                "value": f"**Total:** {stats['earnings'].get('total', 0):,} cowoncy\n"
                        f"**Hunt:** {stats['earnings'].get('hunt', 0):,}\n"
                        f"**Battle:** {stats['earnings'].get('battle', 0):,}\n"
                        f"**Daily:** {stats['earnings'].get('daily', 0):,}",
                "inline": True
            })
        
        # Gambling
        if "gambling" in stats:
            fields.append({
                "name": "🎰 Gambling",
                "value": f"**Wins:** {stats['gambling'].get('wins', 0)}\n"
                        f"**Losses:** {stats['gambling'].get('losses', 0)}\n"
                        f"**Net:** {stats['gambling'].get('net', 0):,}",
                "inline": True
            })
        
        # Rare catches
        if "rare_catches" in stats:
            catches = stats['rare_catches']
            if any(catches.values()):
                fields.append({
                    "name": "🌟 Rare Catches",
                    "value": f"**Mythical:** {catches.get('mythical', 0)}\n"
                            f"**Fabled:** {catches.get('fabled', 0)}\n"
                            f"**Legendary:** {catches.get('legendary', 0)}",
                    "inline": True
                })
        
        # Captchas
        if "captchas" in stats:
            fields.append({
                "name": "🔐 Captchas",
                "value": f"**Solved:** {stats['captchas'].get('solved', 0)}\n"
                        f"**Failed:** {stats['captchas'].get('failed', 0)}",
                "inline": True
            })
        
        # Uptime
        if "uptime" in stats:
            hours = stats['uptime'] // 3600
            minutes = (stats['uptime'] % 3600) // 60
            fields.append({
                "name": "⏱️ Uptime",
                "value": f"{hours}h {minutes}m",
                "inline": True
            })
        
        embed = self.create_embed(
            title="📈 Daily Summary Report",
            description=f"**Account:** {account_name}\n**Date:** {datetime.now().strftime('%Y-%m-%d')}",
            color=0x00D7AF,  # Cyan
            fields=fields,
            footer="Generated by Mizu OwO Bot"
        )
        
        await self.send(embeds=[embed])
        
    async def send_warning(
        self,
        account_name: str,
        warning_type: str,
        message: str
    ):
        """Send warning notification"""
        embed = self.create_embed(
            title=f"⚠️ Warning: {warning_type}",
            description=f"**Account:** {account_name}\n\n{message}",
            color=0xFF9800,  # Orange
            footer="Warning detected by Mizu OwO Bot"
        )
        
        await self.send(embeds=[embed])
        
    async def send_quest_completed(
        self,
        account_name: str,
        quest_name: str,
        progress: str,
        reward: str = None
    ):
        """Send quest completion notification"""
        description = f"**Account:** {account_name}\n**Quest:** {quest_name}\n**Progress:** {progress}"
        
        if reward:
            description += f"\n**Reward:** {reward}"
            
        embed = self.create_embed(
            title="🎉 Quest Completed!",
            description=description,
            color=0x00FF00,  # Green
            footer="Quest tracked by Mizu OwO Bot"
        )
        
        await self.send(embeds=[embed])
        
    async def send_error(
        self,
        account_name: str,
        error_type: str,
        error_message: str,
        traceback: str = None
    ):
        """Send error notification"""
        description = f"**Account:** {account_name}\n**Error Type:** {error_type}\n**Message:** {error_message}"
        
        if traceback:
            description += f"\n\n```\n{traceback[:1000]}\n```"
            
        embed = self.create_embed(
            title="❌ Error Occurred",
            description=description,
            color=0xFF0000,  # Red
            footer="Error logged by Mizu OwO Bot"
        )
        
        await self.send(embeds=[embed])
        
    async def send_status_update(
        self,
        account_name: str,
        status: str,
        message: str,
        color: int = 0x00D7AF
    ):
        """Send general status update"""
        embed = self.create_embed(
            title=f"ℹ️ Status Update: {status}",
            description=f"**Account:** {account_name}\n\n{message}",
            color=color,
            footer="Status update from Mizu OwO Bot"
        )
        
        await self.send(embeds=[embed])
        
    async def send_gems_status(
        self,
        account_name: str,
        gems_available: bool,
        gem_counts: Dict[str, int] = None
    ):
        """Send gems status notification"""
        if gems_available:
            title = "✅ Gems Available"
            description = f"**Account:** {account_name}\n\nGems are now available! Hunt resumed."
            color = 0x00FF00
        else:
            title = "⚠️ No Gems Available"
            description = f"**Account:** {account_name}\n\nRan out of gems! Hunt paused."
            color = 0xFF9800
            
        if gem_counts:
            gem_text = "\n".join([f"• {tier.title()}: {count}" for tier, count in gem_counts.items() if count > 0])
            if gem_text:
                description += f"\n\n**Available Gems:**\n{gem_text}"
                
        embed = self.create_embed(
            title=title,
            description=description,
            color=color,
            footer="Gem status tracked by Mizu OwO Bot"
        )
        
        await self.send(embeds=[embed])


class WebhookManager:
    """Manage multiple webhooks for different notification types"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)
        
        # Different webhooks for different notification types
        main_url = config.get("webhookUrl")
        captcha_url = config.get("webhookCaptchaUrl") or main_url
        
        self.main_webhook = DiscordWebhook(main_url) if main_url else None
        self.captcha_webhook = DiscordWebhook(captcha_url) if captcha_url else None
        
        self.user_id_to_ping = config.get("webhookUserIdToPingOnCaptcha")
        
    def is_enabled(self, notification_type: str = None) -> bool:
        """Check if webhooks are enabled"""
        if not self.enabled or not self.main_webhook:
            return False
            
        if notification_type:
            return self.config.get(f"notify{notification_type.title()}", True)
            
        return True
        
    async def send_notification(self, notification_type: str, **kwargs):
        """Send notification based on type"""
        if not self.is_enabled(notification_type):
            return
            
        try:
            if notification_type == "captcha" and self.captcha_webhook:
                await self.captcha_webhook.send_captcha_alert(
                    user_id_to_ping=self.user_id_to_ping,
                    **kwargs
                )
            elif notification_type == "ban":
                await self.main_webhook.send_ban_alert(
                    user_id_to_ping=self.user_id_to_ping,
                    **kwargs
                )
            elif notification_type == "rare_catch":
                await self.main_webhook.send_rare_catch(**kwargs)
            elif notification_type == "daily_summary":
                await self.main_webhook.send_daily_summary(**kwargs)
            elif notification_type == "warning":
                await self.main_webhook.send_warning(**kwargs)
            elif notification_type == "quest_completed":
                await self.main_webhook.send_quest_completed(**kwargs)
            elif notification_type == "error":
                await self.main_webhook.send_error(**kwargs)
            elif notification_type == "gems_status":
                await self.main_webhook.send_gems_status(**kwargs)
            elif notification_type == "status":
                await self.main_webhook.send_status_update(**kwargs)
                
        except Exception as e:
            print(f"Webhook notification error: {e}")
            
    async def close(self):
        """Close all webhook sessions"""
        if self.main_webhook:
            await self.main_webhook.close()
        if self.captcha_webhook and self.captcha_webhook != self.main_webhook:
            await self.captcha_webhook.close()

