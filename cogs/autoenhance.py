import asyncio
import time
import re
from discord.ext import commands, tasks
from discord.ext.commands import ExtensionNotLoaded


class AutoEnhance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_gem_use_time = 0
        self.last_essence_invest_time = 0
        self.waiting_for_inventory = False
        self.waiting_for_huntbot_info = False
        self.available_gems = None
        self.essence_balance = 0
        
        # Commands
        self.inv_cmd = {
            "cmd_name": self.bot.alias["inv"]["normal"],
            "prefix": True,
            "checks": True,
            "id": "autoenhance_inv"
        }
        
        self.gem_cmd = {
            "cmd_name": self.bot.alias["use"]["normal"],
            "cmd_arguments": "",
            "prefix": True,
            "checks": False,
            "id": "autoenhance_gems"
        }
        
        self.huntbot_cmd = {
            "cmd_name": self.bot.alias["huntbot"]["normal"],
            "prefix": True,
            "checks": True,
            "id": "autoenhance_huntbot"
        }
        
        self.upgrade_cmd = {
            "cmd_name": self.bot.alias["upgrade"]["normal"],
            "cmd_arguments": "",
            "prefix": True,
            "checks": False,
            "id": "autoenhance_upgrade"
        }

    async def cog_load(self):
        config = self.bot.settings_dict.get("autoEnhance", {})
        if config.get("enabled", False):
            self.auto_enhance_loop.start()
            await self.bot.log("AutoEnhance system loaded and started!", "#9c88ff")
        else:
            await self.bot.log("AutoEnhance system is disabled in settings.", "#9c88ff")

    async def cog_unload(self):
        self.auto_enhance_loop.cancel()
        await self.bot.remove_queue(id="autoenhance_inv")
        await self.bot.remove_queue(id="autoenhance_gems")
        await self.bot.remove_queue(id="autoenhance_huntbot")
        await self.bot.remove_queue(id="autoenhance_upgrade")
        await self.bot.log("AutoEnhance system unloaded.", "#9c88ff")

    @tasks.loop(minutes=5)  # Check every 5 minutes
    async def auto_enhance_loop(self):
        """Main loop for auto enhancement features."""
        try:
            config = self.bot.settings_dict.get("autoEnhance", {})
            if not config.get("enabled", False):
                return
                
            current_time = time.time()
            
            # Auto use gems when hunting
            if (config.get("autoUseGems", {}).get("enabled", False) and 
                current_time - self.last_gem_use_time > config.get("autoUseGems", {}).get("cooldownMinutes", 10) * 60):
                await self.check_and_use_gems()
                
            # Auto invest essence for efficiency duration
            if (config.get("autoInvestEssence", {}).get("enabled", False) and
                current_time - self.last_essence_invest_time > config.get("autoInvestEssence", {}).get("cooldownMinutes", 30) * 60):
                await self.check_and_invest_essence()
                
        except Exception as e:
            await self.bot.log(f"Error in AutoEnhance loop: {e}", "#c25560")

    @auto_enhance_loop.before_loop
    async def before_auto_enhance_loop(self):
        await self.bot.wait_until_ready()

    async def check_and_use_gems(self):
        """Check inventory and use gems if available."""
        try:
            config = self.bot.settings_dict.get("autoEnhance", {}).get("autoUseGems", {})
            
            if not config.get("enabled", False):
                return
                
            # Only use gems if hunt is enabled
            if not self.bot.settings_dict.get("commands", {}).get("hunt", {}).get("enabled", False):
                return
                
            await self.bot.log("AutoEnhance: Checking for available gems...", "#9c88ff")
            self.waiting_for_inventory = True
            await self.bot.put_queue(self.inv_cmd, priority=True)
            
        except Exception as e:
            await self.bot.log(f"Error checking gems: {e}", "#c25560")

    async def check_and_invest_essence(self):
        """Check huntbot stats and invest essence for efficiency/duration."""
        try:
            config = self.bot.settings_dict.get("autoEnhance", {}).get("autoInvestEssence", {})
            
            if not config.get("enabled", False):
                return
                
            # Only invest if huntbot is enabled
            if not self.bot.settings_dict.get("commands", {}).get("autoHuntBot", {}).get("enabled", False):
                return
                
            await self.bot.log("AutoEnhance: Checking huntbot stats for essence investment...", "#9c88ff")
            self.waiting_for_huntbot_info = True
            await self.bot.put_queue(self.huntbot_cmd, priority=True)
            
        except Exception as e:
            await self.bot.log(f"Error checking essence investment: {e}", "#c25560")

    def find_gems_available(self, message):
        """Parse inventory message to find available gems."""
        gem_tiers = {
            "common": ["051", "065", "072", "079"],
            "uncommon": ["052", "066", "073", "080"],
            "rare": ["053", "067", "074", "081"],
            "epic": ["054", "068", "075", "082"],
            "mythical": ["055", "069", "076", "083"],
            "legendary": ["056", "070", "077", "084"],
            "fabled": ["057", "071", "078", "085"],
        }
        
        available_gems = {
            "fabled": {"057": 0, "071": 0, "078": 0, "085": 0},
            "legendary": {"056": 0, "070": 0, "077": 0, "084": 0},
            "mythical": {"055": 0, "069": 0, "076": 0, "083": 0},
            "epic": {"054": 0, "068": 0, "075": 0, "082": 0},
            "rare": {"053": 0, "067": 0, "074": 0, "081": 0},
            "uncommon": {"052": 0, "066": 0, "073": 0, "080": 0},
            "common": {"051": 0, "065": 0, "072": 0, "079": 0},
        }
        
        # Convert small numbers to normal numbers
        def convert_small_numbers(small_number):
            numbers = {
                "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
                "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
            }
            # Only convert superscript numbers, filter out other characters
            converted = ''.join(numbers.get(char, '') for char in small_number if char in numbers)
            # If no valid numbers found, return 0
            return int(converted) if converted else 0
        
        inv_numbers = re.findall(r"`(\d+)`.*?([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", message)
        for gem_id, small_number in inv_numbers:
            gem_count = convert_small_numbers(small_number)
            for tier, gems in available_gems.items():
                if gem_id in gems:
                    gems[gem_id] = gem_count
                    
        return available_gems

    def find_gems_to_use(self, available_gems):
        """Find the best gems to use based on configuration."""
        config = self.bot.settings_dict.get("autoEnhance", {}).get("autoUseGems", {})
        
        gem_types = {
            0: "huntGem",      # Hunt gems
            1: "empoweredGem", # Empowered gems
            2: "luckyGem",     # Lucky gems
            3: "specialGem"    # Special gems
        }
        
        tier_order = ['fabled', 'legendary', 'mythical', 'epic', 'rare', 'uncommon', 'common']
        
        # Use lowest to highest priority if configured
        if config.get("useLowestFirst", True):
            tier_order.reverse()
            
        gem_tiers = {
            "common": ["051", "065", "072", "079"],
            "uncommon": ["052", "066", "073", "080"], 
            "rare": ["053", "067", "074", "081"],
            "epic": ["054", "068", "075", "082"],
            "mythical": ["055", "069", "076", "083"],
            "legendary": ["056", "070", "077", "084"],
            "fabled": ["057", "071", "078", "085"],
        }
        
        gems_to_use = []
        
        for tier in tier_order:
            if not config.get("tiers", {}).get(tier, True):
                continue
                
            for gem_id in gem_tiers[tier]:
                gem_index = gem_tiers[tier].index(gem_id)
                gem_type_key = gem_types[gem_index]
                
                if (config.get("gemTypes", {}).get(gem_type_key, True) and 
                    available_gems[tier].get(gem_id, 0) > 0):
                    gems_to_use.append(gem_id)
                    
            # Use only one tier at a time
            if gems_to_use:
                break
                
        return gems_to_use

    def parse_huntbot_stats(self, embed):
        """Parse huntbot embed to get essence and efficiency stats."""
        try:
            if not embed.fields:
                return None
                
            stats = {}
            for field in embed.fields:
                if "essence" in field.name.lower():
                    # Extract essence amount
                    essence_match = re.search(r'(\d+)', field.value)
                    if essence_match:
                        stats['essence'] = int(essence_match.group(1))
                        
                elif "efficiency" in field.name.lower():
                    # Extract efficiency level
                    eff_match = re.search(r'(\d+)', field.value)
                    if eff_match:
                        stats['efficiency_level'] = int(eff_match.group(1))
                        
                elif "duration" in field.name.lower():
                    # Extract duration level
                    dur_match = re.search(r'(\d+)', field.value)
                    if dur_match:
                        stats['duration_level'] = int(dur_match.group(1))
                        
            return stats
            
        except Exception as e:
            print(f"Error parsing huntbot stats: {e}")
            return None

    async def invest_essence(self, stats):
        """Invest essence based on configuration."""
        try:
            config = self.bot.settings_dict.get("autoEnhance", {}).get("autoInvestEssence", {})
            
            essence_available = stats.get('essence', 0)
            min_essence_required = config.get("minEssenceRequired", 100)
            
            if essence_available < min_essence_required:
                await self.bot.log(f"AutoEnhance: Not enough essence ({essence_available} < {min_essence_required})", "#9c88ff")
                return
                
            # Determine investment priorities
            efficiency_level = stats.get('efficiency_level', 0)
            duration_level = stats.get('duration_level', 0)
            
            max_efficiency = config.get("maxEfficiencyLevel", 50)
            max_duration = config.get("maxDurationLevel", 50)
            
            # Invest in efficiency first if below max
            if efficiency_level < max_efficiency:
                investment_amount = min(essence_available // 2, config.get("maxInvestmentPerTime", 50))
                if investment_amount > 0:
                    self.upgrade_cmd["cmd_arguments"] = f"efficiency {investment_amount}"
                    await self.bot.put_queue(self.upgrade_cmd, priority=True)
                    await self.bot.log(f"AutoEnhance: Investing {investment_amount} essence in efficiency", "#9c88ff")
                    await asyncio.sleep(2)
                    
            # Invest remaining in duration if below max
            if duration_level < max_duration and essence_available > investment_amount:
                remaining_essence = essence_available - investment_amount
                duration_investment = min(remaining_essence, config.get("maxInvestmentPerTime", 50))
                if duration_investment > 0:
                    self.upgrade_cmd["cmd_arguments"] = f"duration {duration_investment}"
                    await self.bot.put_queue(self.upgrade_cmd, priority=True)
                    await self.bot.log(f"AutoEnhance: Investing {duration_investment} essence in duration", "#9c88ff")
                    
            self.last_essence_invest_time = time.time()
            
        except Exception as e:
            await self.bot.log(f"Error investing essence: {e}", "#c25560")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for OwO bot responses."""
        if message.channel.id != self.bot.channel_id or message.author.id != self.bot.owo_bot_id:
            return
            
        try:
            # Handle inventory response for gems
            if self.waiting_for_inventory and "'s Inventory ======**" in message.content:
                self.waiting_for_inventory = False
                await self.bot.remove_queue(id="autoenhance_inv")
                
                self.available_gems = self.find_gems_available(message.content)
                gems_to_use = self.find_gems_to_use(self.available_gems)
                
                if gems_to_use:
                    gem_args = " ".join([gem_id[1:] for gem_id in gems_to_use])  # Remove first digit
                    self.gem_cmd["cmd_arguments"] = gem_args
                    await self.bot.put_queue(self.gem_cmd, priority=True)
                    await self.bot.log(f"AutoEnhance: Using gems: {gem_args}", "#9c88ff")
                    self.last_gem_use_time = time.time()
                else:
                    await self.bot.log("AutoEnhance: No suitable gems found to use", "#9c88ff")
                    
            # Handle huntbot response for essence investment
            elif self.waiting_for_huntbot_info and message.embeds:
                for embed in message.embeds:
                    if embed.author and "'s huntbot" in embed.author.name.lower():
                        self.waiting_for_huntbot_info = False
                        await self.bot.remove_queue(id="autoenhance_huntbot")
                        
                        stats = self.parse_huntbot_stats(embed)
                        if stats:
                            await self.invest_essence(stats)
                        else:
                            await self.bot.log("AutoEnhance: Could not parse huntbot stats", "#9c88ff")
                        break
                        
            # Handle gem use confirmations
            elif "You used" in message.content and any(gem_type in message.content.lower() for gem_type in ["hunt", "luck", "empowered", "special"]):
                await self.bot.remove_queue(id="autoenhance_gems")
                await self.bot.log("AutoEnhance: Gems used successfully!", "#51cf66")
                
            # Handle upgrade confirmations  
            elif "upgraded" in message.content.lower() and any(trait in message.content.lower() for trait in ["efficiency", "duration"]):
                await self.bot.remove_queue(id="autoenhance_upgrade")
                await self.bot.log("AutoEnhance: Essence invested successfully!", "#51cf66")
                
        except Exception as e:
            await self.bot.log(f"Error in AutoEnhance on_message: {e}", "#c25560")


async def setup(bot):
    await bot.add_cog(AutoEnhance(bot))
