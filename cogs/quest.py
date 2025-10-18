import asyncio
import re
from datetime import datetime, timezone
from discord.ext import commands, tasks
from discord.ext.commands import ExtensionNotLoaded

class Quest(commands.Cog):
    """Quest Tracker - Auto-detect and track OwO daily quests."""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Quest tracking data
        self.quests = {
            "hunt": {"target": 0, "progress": 0, "completed": False},
            "battle": {"target": 0, "progress": 0, "completed": False},
            "owo": {"target": 0, "progress": 0, "completed": False},
            "pray": {"target": 0, "progress": 0, "completed": False},
            "curse": {"target": 0, "progress": 0, "completed": False},
            "gamble": {"target": 0, "progress": 0, "completed": False},
            "action": {"target": 0, "progress": 0, "completed": False},
            "emoji": {"target": 0, "progress": 0, "completed": False},
            "special": {"target": 0, "progress": 0, "completed": False}
        }
        
        # Rare animal catches
        self.rare_catches = {
            "mythical": [],
            "fabled": [],
            "legendary": []
        }
        
        # Quest command
        self.quest_cmd = {
            "cmd_name": "checklist",
            "cmd_arguments": "",
            "prefix": True,
            "checks": False,
            "id": "quest"
        }
        
        self.last_quest_check = 0
        self.quest_detected = False
        
    async def cog_load(self):
        """Load the cog and start quest checker if enabled."""
        config = self.bot.settings_dict.get("questTracker", {})
        
        if not config.get("enabled", False):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.quest"))
            except ExtensionNotLoaded:
                pass
            return
            
        await self.bot.log("Quest Tracker loaded - Will auto-check daily quests!", "#00d7af")
        self.daily_quest_check.start()
        
    async def cog_unload(self):
        """Unload the cog and stop quest checker."""
        if hasattr(self, 'daily_quest_check'):
            self.daily_quest_check.cancel()
        await self.bot.log("Quest Tracker unloaded.", "#00d7af")
        
    @tasks.loop(hours=6)
    async def daily_quest_check(self):
        """Check quests every 6 hours to ensure we have latest data."""
        try:
            config = self.bot.settings_dict.get("questTracker", {})
            if not config.get("autoCheckQuests", True):
                return
                
            await self.bot.log("Quest Tracker: Checking daily quests...", "#00d7af")
            await self.bot.put_queue(self.quest_cmd, priority=False)
            
        except Exception as e:
            await self.bot.log(f"Error in daily quest check: {e}", "#c25560")
            
    @daily_quest_check.before_loop
    async def before_daily_quest_check(self):
        """Wait for bot to be ready before starting loop."""
        await self.bot.wait_until_ready()
        # Wait a bit for bot to initialize
        await asyncio.sleep(30)
        
    def parse_quest_from_checklist(self, message):
        """Parse quest requirements from OwO checklist embed."""
        try:
            if not message.embeds:
                return
                
            embed = message.embeds[0]
            description = embed.description or ""
            
            # Reset quests
            for quest_type in self.quests:
                self.quests[quest_type] = {"target": 0, "progress": 0, "completed": False}
            
            # Parse each quest line
            quest_patterns = {
                "hunt": r"(?:hunt|catch)\s+(\d+)\s+(?:animals?|times?)",
                "battle": r"(?:battle|fight)\s+(\d+)\s+(?:animals?|times?)",
                "owo": r"(?:say|type)\s+(?:owo|uwu)\s+(\d+)\s+times?",
                "pray": r"pray\s+(\d+)\s+times?",
                "curse": r"curse\s+(\d+)\s+times?",
                "gamble": r"(?:gamble|bet)\s+(\d+)\s+times?",
                "action": r"(?:run|pup|piku)\s+(\d+)\s+times?",
                "emoji": r"send\s+(\d+)\s+(?:emojis?|emoji)",
                "special": r"(?:use|spend)\s+(\d+)\s+(?:special|gem|lootbox)"
            }
            
            for quest_type, pattern in quest_patterns.items():
                match = re.search(pattern, description, re.IGNORECASE)
                if match:
                    target = int(match.group(1))
                    self.quests[quest_type]["target"] = target
                    
            # Check for already completed quests (has ✅)
            for quest_type in self.quests:
                if self.quests[quest_type]["target"] > 0:
                    # Look for completion marker
                    if f"✅" in description or "completed" in description.lower():
                        quest_line = re.search(rf"{quest_type}.*?✅", description, re.IGNORECASE)
                        if quest_line:
                            self.quests[quest_type]["completed"] = True
                            self.quests[quest_type]["progress"] = self.quests[quest_type]["target"]
                            
            self.quest_detected = True
            return True
            
        except Exception as e:
            await self.bot.log(f"Error parsing quest checklist: {e}", "#c25560")
            return False
            
    async def update_quest_progress(self, quest_type, amount=1):
        """Update quest progress and check if completed."""
        try:
            if quest_type not in self.quests:
                return
                
            quest = self.quests[quest_type]
            
            # Skip if no target set or already completed
            if quest["target"] == 0 or quest["completed"]:
                return
                
            # Update progress
            quest["progress"] = min(quest["progress"] + amount, quest["target"])
            
            # Check if just completed
            if quest["progress"] >= quest["target"] and not quest["completed"]:
                quest["completed"] = True
                
                config = self.bot.settings_dict.get("questTracker", {})
                if config.get("notifications", True):
                    await self.bot.log(
                        f"🎉 Quest Completed: {quest_type.upper()} ({quest['progress']}/{quest['target']})",
                        "#00ff00"
                    )
                    
        except Exception as e:
            await self.bot.log(f"Error updating quest progress: {e}", "#c25560")
            
    def log_rare_catch(self, rarity, animal_name):
        """Log rare animal catches."""
        try:
            rarity_lower = rarity.lower()
            if rarity_lower not in self.rare_catches:
                return
                
            catch_data = {
                "name": animal_name,
                "timestamp": datetime.now(timezone.utc).timestamp()
            }
            
            self.rare_catches[rarity_lower].append(catch_data)
            
            config = self.bot.settings_dict.get("questTracker", {})
            if config.get("logRareAnimals", True):
                asyncio.create_task(
                    self.bot.log(
                        f"🌟 {rarity.upper()} caught: {animal_name}!",
                        "#ffd43b"
                    )
                )
                
        except Exception as e:
            asyncio.create_task(self.bot.log(f"Error logging rare catch: {e}", "#c25560"))
            
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for OwO bot responses to track quest progress."""
        if message.channel.id != self.bot.cm.id or message.author.id != self.bot.owo_bot_id:
            return
            
        try:
            config = self.bot.settings_dict.get("questTracker", {})
            if not config.get("enabled", False):
                return
                
            # Parse checklist
            if message.embeds and "checklist" in message.content.lower():
                if self.parse_quest_from_checklist(message):
                    await self.bot.log("Quest Tracker: Daily quests detected!", "#00d7af")
                    
                    # Log active quests
                    active_quests = [
                        f"{qt}: {qd['target']}" 
                        for qt, qd in self.quests.items() 
                        if qd['target'] > 0
                    ]
                    if active_quests:
                        await self.bot.log(
                            f"Active Quests: {', '.join(active_quests)}",
                            "#00d7af"
                        )
                    return
                    
            # Track hunt/battle progress
            if "and caught a" in message.content or "🌱" in message.content:
                await self.update_quest_progress("hunt", 1)
                
                # Check for rare animals
                if "✨ **MYTHICAL**" in message.content:
                    animal_match = re.search(r"caught a \*\*(.+?)\*\*", message.content)
                    if animal_match:
                        self.log_rare_catch("mythical", animal_match.group(1))
                elif "🌟 **FABLED**" in message.content:
                    animal_match = re.search(r"caught a \*\*(.+?)\*\*", message.content)
                    if animal_match:
                        self.log_rare_catch("fabled", animal_match.group(1))
                elif "✨ **LEGENDARY**" in message.content:
                    animal_match = re.search(r"caught a \*\*(.+?)\*\*", message.content)
                    if animal_match:
                        self.log_rare_catch("legendary", animal_match.group(1))
                        
            if "and caught a" in message.content or "⚔" in message.content:
                await self.update_quest_progress("battle", 1)
                
            # Track owo/uwu
            if "owo" in message.content.lower() or "uwu" in message.content.lower():
                if message.author.id == self.bot.user.id:
                    await self.update_quest_progress("owo", 1)
                    
            # Track pray/curse
            if "prayed for" in message.content or "🙏" in message.content:
                await self.update_quest_progress("pray", 1)
            if "cursed" in message.content and "😈" in message.content:
                await self.update_quest_progress("curse", 1)
                
            # Track gambling (coinflip/slots)
            if ("flipped" in message.content and "won" in message.content) or \
               ("flipped" in message.content and "lost" in message.content):
                await self.update_quest_progress("gamble", 1)
            if "spent" in message.content and "slot machine" in message.content:
                await self.update_quest_progress("gamble", 1)
                
            # Track action commands (run/pup/piku)
            if any(cmd in message.content.lower() for cmd in ["you ran", "you pup", "you piku"]):
                await self.update_quest_progress("action", 1)
                
        except Exception as e:
            await self.bot.log(f"Error in quest tracker message handler: {e}", "#c25560")
            
    def get_quest_status(self):
        """Get current quest status for dashboard."""
        return {
            "quests": self.quests,
            "rare_catches": {
                "mythical": len(self.rare_catches["mythical"]),
                "fabled": len(self.rare_catches["fabled"]),
                "legendary": len(self.rare_catches["legendary"])
            },
            "detected": self.quest_detected
        }

async def setup(bot):
    await bot.add_cog(Quest(bot))

