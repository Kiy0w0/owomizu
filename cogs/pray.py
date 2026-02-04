"""
Mizu OwO Bot
Copyright (C) 2025 MizuNetwork
Copyright (C) 2025 Kiy0w0
"""

import asyncio
import random
from discord.ext import commands, tasks

def cmd_argument(userid, ping):
    if userid:
        return f"<@{random.choice(userid)}>" if ping else random.choice(userid)
    else:
        return ""

class Pray(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pray_cmd = {
            "cmd_name": "pray",
            "cmd_arguments": None,
            "prefix": True,
            "checks": True,
            "id": "pray"
        }
        self.curse_cmd = {
            "cmd_name": "curse",
            "cmd_arguments": None,
            "prefix": True,
            "checks": True,
            "id": "pray" # Use same ID queue
        }

    async def cog_load(self):
        self.pray_loop.start()
        await self.bot.log("Pray/Curse system loaded [@echoquill needs coffee]", "blue")

    async def cog_unload(self):
        self.pray_loop.cancel()
        await self.bot.remove_queue(id="pray")

    @tasks.loop()
    async def pray_loop(self):
        # Tunggu sampai bot siap
        await self.bot.wait_until_ready()
        
        # DEBUG LOG
        # await self.bot.log(f"DEBUG: Pray Loop Tick. Enabled: {self.bot.settings_dict['commands']['pray']['enabled']} / {self.bot.settings_dict['commands']['curse']['enabled']}", "#555555")

        # Cek apakah reaction bot handler aktif
        if self.bot.settings_dict["defaultCooldowns"]["reactionBot"]["pray_and_curse"]:
            await self.bot.log("DEBUG: Pray Loop Cancelled due to reactionBot setting", "#ff0000")
            self.pray_loop.cancel()
            return
            
        cmds_enabled = []
        if self.bot.settings_dict['commands']['pray']['enabled']:
            cmds_enabled.append("pray")
        if self.bot.settings_dict['commands']['curse']['enabled']:
            cmds_enabled.append("curse")
            
        if not cmds_enabled:
            await self.bot.log("Pray/Curse disabled in settings. Stopping loop.", "#d0ff78")
            self.pray_loop.cancel()
            return

        # Pilih command random
        chosen_cmd = random.choice(cmds_enabled)
        cnf = self.bot.settings_dict['commands'][chosen_cmd]
        
        # Siapkan argumen (user target)
        cmd_argument_data = cmd_argument(cnf['userid'], cnf['pingUser'])
        
        # update command object
        if chosen_cmd == "pray":
            self.pray_cmd["cmd_arguments"] = cmd_argument_data
            target_cmd_obj = self.pray_cmd
        else:
            self.curse_cmd["cmd_arguments"] = cmd_argument_data
            target_cmd_obj = self.curse_cmd

        # Masukkan ke queue
        await self.bot.put_queue(target_cmd_obj, priority=True)
        await self.bot.log(f"Queued {chosen_cmd}... (Wait {cnf['cooldown']})", "#d0ff78")

        # Sleep sesuai cooldown
        sleep_duration = self.bot.random_float(cnf["cooldown"]) 
        await self.bot.sleep_till([sleep_duration, sleep_duration + 5])

    @pray_loop.before_loop
    async def before_pray(self):
        await self.bot.wait_until_ready()
        # Delay awal sedikit agar tidak bentrok pas login
        await asyncio.sleep(random.randint(5, 15))

async def setup(bot):
    await bot.add_cog(Pray(bot))
