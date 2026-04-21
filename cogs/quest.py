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

        self.regex_title = re.compile(r"\*\*\d+\.\s(.+?)\*\*")
        self.regex_progress = re.compile(r"Progress:\s*\[(\d+)/(\d+)\]")
        self.regex_locked = re.compile(r"🔒 Locked")

        self.quest_channel_id = self.bot.channel_id

    async def cog_load(self):
        if not self.bot.settings_dict.get("questTracker", {}).get("enabled", True):
             await self.bot.log("Quest System disabled (enable questTracker to use)", "#9dc3f5")
        else:
            await self.bot.log("Quest Automation System Loaded 📜", "#51cf66")
            self.bot.loop.create_task(self.quest_loop())

    async def quest_loop(self):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            while (
                self.bot.command_handler_status["captcha"] 
                or not self.bot.command_handler_status["state"]
                or self.bot.command_handler_status["sleep"]
            ):
                await asyncio.sleep(10)

            try:
                await self.check_quest()

                if self.current_quest and not self.current_quest['is_locked'] and not self.current_quest['finished']:
                    await self.solve_quest(self.current_quest)

                sleep_time = self.bot.random.uniform(300, 600)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                await self.bot.log(f"Quest Loop Error: {e}", "#c25560")
                await asyncio.sleep(60)

    async def check_quest(self):

        cmd = {
            "cmd_name": "owo",
            "cmd_arguments": "quest",
            "prefix": False,
            "id": "quest_check"
        }
        await self.bot.put_queue(cmd)

        self.current_quest = None

        await asyncio.sleep(5) 

    async def solve_quest(self, quest):

        title = quest['title'].lower()
        pro_current = quest['progress_current']
        pro_target = quest['progress_target']

        if pro_current >= pro_target:
            return

        action_cmd = None

        if "say 'owo'" in title:
            action_cmd = "owo"
        elif "gamble" in title:
            action_cmd = "owo cf 1 h" 
        elif "use an action command" in title:
            action_cmd = f"owo hug <@{self.bot.user.id}>"

        if action_cmd:
            await self.bot.log(f"Quest Action: {title} ({pro_current}/{pro_target})", "#9b59b6")

            cmd = {
                "cmd_name": action_cmd.split()[0],
                "cmd_arguments": " ".join(action_cmd.split()[1:]),
                "id": "quest_action",
                "prefix": False
            }

            if action_cmd.startswith("owo "):
                cmd["cmd_name"] = "owo"
                cmd["cmd_arguments"] = action_cmd[4:]

            await self.bot.put_queue(cmd)

            await asyncio.sleep(self.bot.random.uniform(15, 25))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.owo_bot_id:
            return

        if message.channel.id != self.quest_channel_id:
            return

        if not message.embeds:
            return

        embed = message.embeds[0]

        if embed.author and "Quest Log" in embed.author.name:
            desc = embed.description
            if not desc:
                return

            if "You finished all of your quests!" in desc:
                self.current_quest = {'finished': True, 'title': 'All Done'}
                return

            lines = desc.split('\n')

            found_quest = None

            for line in lines:
                if not line.strip(): continue

                if "🔒 Locked" in line:
                    continue

                title_match = self.regex_title.search(line)
                if not title_match: continue
                title = title_match.group(1)

                prog_match = self.regex_progress.search(line)
                if not prog_match: continue

                curr = int(prog_match.group(1))
                target = int(prog_match.group(2))

                if curr < target:
                    found_quest = {
                        'title': title,
                        'progress_current': curr,
                        'progress_target': target,
                        'is_locked': False,
                        'finished': False
                    }
                    break 

            if found_quest:
                self.current_quest = found_quest
            else:
                self.current_quest = None

async def setup(bot):
    await bot.add_cog(Quest(bot))