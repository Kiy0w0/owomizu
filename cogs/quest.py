import re
import asyncio
import time
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

class Quest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = False
        self.current_quest = None
        self.quest_msg_id = None
        self.max_retries = 3
        
        # Regex Patterns (Ported from tetaver)
        self.regex_title = re.compile(r"\*\*\d+\.\s(.+?)\*\*")
        self.regex_progress = re.compile(r"Progress:\s*\[(\d+)/(\d+)\]")
        self.regex_locked = re.compile(r"🔒 Locked")
        
        # Configuration defaults (will use settings.json later)
        self.quest_channel_id = self.bot.channel_id # Default to farming channel

    async def cog_load(self):
        # Check settings.json (we might need to add "quest" section later)
        if not self.bot.settings_dict.get("questTracker", {}).get("enabled", True): # Using questTracker config for now
             await self.bot.log("Quest System disabled (enable questTracker to use)", "#9dc3f5")
             # We don't unload because functionality might be mixed, 
             # but we won't run the auto-loop
        else:
            await self.bot.log("Quest Automation System Loaded 📜", "#51cf66")
            self.bot.loop.create_task(self.quest_loop())

    async def quest_loop(self):
        """Main loop to check and perform quests"""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            # Wait for other priority tasks
            while (
                self.bot.command_handler_status["captcha"] 
                or not self.bot.command_handler_status["state"]
                or self.bot.command_handler_status["sleep"]
            ):
                await asyncio.sleep(10)

            try:
                # 1. Check Quest Log
                await self.check_quest()
                
                # 2. If active quest found, perform action
                if self.current_quest and not self.current_quest['is_locked'] and not self.current_quest['finished']:
                    await self.solve_quest(self.current_quest)
                
                # Wait before next check (e.g., 5-10 minutes)
                sleep_time = self.bot.random.uniform(300, 600)
                # await self.bot.log(f"Quest: Sleeping {int(sleep_time)}s before next check", "#6F7C8A")
                await asyncio.sleep(sleep_time)

            except Exception as e:
                await self.bot.log(f"Quest Loop Error: {e}", "#c25560")
                await asyncio.sleep(60)

    async def check_quest(self):
        """Send 'owo quest' and parse the response"""
        
        # Use put_queue to send command
        cmd = {
            "cmd_name": "owo",
            "cmd_arguments": "quest",
            "prefix": False,
            "id": "quest_check"
        }
        await self.bot.put_queue(cmd)
        
        # Reset current quest state to trigger a refresh
        self.current_quest = None
        
        # Wait a bit for the message to arrive and be parsed
        await asyncio.sleep(5) 

    async def solve_quest(self, quest):
        """Decide what to do based on quest title"""
        title = quest['title'].lower()
        pro_current = quest['progress_current']
        pro_target = quest['progress_target']
        
        if pro_current >= pro_target:
            return

        action_cmd = None
        
        # Logic Mapping
        if "say 'owo'" in title:
            action_cmd = "owo"
        elif "gamble" in title:
            # Safe gamble: coinflip 1 cowoncy
            action_cmd = "owo cf 1 h" 
        elif "use an action command" in title:
            # Hug self or random
            action_cmd = f"owo hug <@{self.bot.user.id}>"
        
        # Complex/Duo quests (Not implemented yet)
        # elif "battle with a friend" in title: ...
        # elif "have a friend curse you" in title: ...

        if action_cmd:
            await self.bot.log(f"Quest Action: {title} ({pro_current}/{pro_target})", "#9b59b6")
            
            # Execute the command
            # We use put_queue to respect global delays
            cmd = {
                "cmd_name": action_cmd.split()[0], # e.g., 'owo'
                "cmd_arguments": " ".join(action_cmd.split()[1:]),
                "id": "quest_action",
                "prefix": False # We included 'owo' in action_cmd for clarity, but logic might vary
            }
            
            # Fix: cmd_name should be the command, arguments the rest.
            if action_cmd.startswith("owo "):
                cmd["cmd_name"] = "owo"
                cmd["cmd_arguments"] = action_cmd[4:]
            
            # Send the command
            await self.bot.put_queue(cmd)
            
            # Wait a bit to avoid spamming too fast if loop runs tight
            await asyncio.sleep(self.bot.random.uniform(15, 25))

    @commands.Cog.listener()
    async def on_message(self, message):
        # Filter for OwO Bot messages in our channel
        if message.author.id != self.bot.owo_bot_id:
            return
        
        if message.channel.id != self.quest_channel_id:
            return

        if not message.embeds:
            return

        embed = message.embeds[0]
        
        # Detect Quest Log
        if embed.author and "Quest Log" in embed.author.name:
            # Parse the description
            desc = embed.description
            if not desc:
                return

            # Special case: All finished
            if "You finished all of your quests!" in desc:
                self.current_quest = {'finished': True, 'title': 'All Done'}
                # await self.bot.log("Quest: All quests completed! 🎉", "#51cf66")
                return

            # Parse lines
            # Example line: `**1. Say 'owo' 3 times**` ... `Progress: [1/3]`
            lines = desc.split('\n')
            
            found_quest = None
            
            for line in lines:
                if not line.strip(): continue
                
                # Check locked
                if "🔒 Locked" in line:
                    continue
                
                # Extract Title
                title_match = self.regex_title.search(line)
                if not title_match: continue
                title = title_match.group(1)
                
                # Extract Progress
                prog_match = self.regex_progress.search(line)
                if not prog_match: continue
                
                curr = int(prog_match.group(1))
                target = int(prog_match.group(2))
                
                if curr < target:
                    # Found an unfinished, unlocked quest!
                    found_quest = {
                        'title': title,
                        'progress_current': curr,
                        'progress_target': target,
                        'is_locked': False,
                        'finished': False
                    }
                    # We pick the first one we find for now (Priority can be added later)
                    break 
            
            if found_quest:
                self.current_quest = found_quest
                # await self.bot.log(f"Quest Detected: {found_quest['title']} [{found_quest['progress_current']}/{found_quest['progress_target']}]", "#3498db")
            else:
                self.current_quest = None

async def setup(bot):
    await bot.add_cog(Quest(bot))
