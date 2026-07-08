import asyncio
import time

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded


class PupikuFarmer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._startup_done = False
        
        self._tracker = {
            "pup": {"sent_at": 0.0, "replied_at": 0.0},
            "piku": {"sent_at": 0.0, "replied_at": 0.0},
        }

    def _cfg(self, cmd_id: str):
        return self.bot.settings_dict.get("commands", {}).get(cmd_id, {})

    def _build_cmd(self, cmd_id: str):
        return {
            "cmd_name": cmd_id,
            "prefix": True,
            "checks": self._startup_done,
            "id": cmd_id,
        }

    def _mark_sent(self, cmd_id: str):
        self._tracker[cmd_id]["sent_at"] = time.monotonic()

    def _validate_response(self, cmd_id: str) -> bool:
        now = time.monotonic()
        sent_time = self._tracker[cmd_id]["sent_at"]
        last_reply = self._tracker[cmd_id]["replied_at"]

        if sent_time <= 0:
            return False

        if last_reply > 0 and (now - last_reply) < 60:
            return False

        gap = now - sent_time
        if gap < 0 or gap > 12:
            return False

        self._tracker[cmd_id]["replied_at"] = now
        return True

    async def cog_load(self):
        pup_on = self._cfg("pup").get("enabled", False)
        piku_on = self._cfg("piku").get("enabled", False)
        
        if not (pup_on or piku_on):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.pupiku"))
            except ExtensionNotLoaded:
                pass
            return
            
        asyncio.create_task(self._dispatch_cycle(is_startup=True))

    async def cog_unload(self):
        await self.bot.remove_queue(id="pup")
        await self.bot.remove_queue(id="piku")

    async def _dispatch_cycle(self, is_startup=False, target_cmd=None, wait_till_next_day=False):
        if is_startup:
            while not self._startup_done:
                short_cd = self.bot.settings_dict["defaultCooldowns"]["shortCooldown"]
                await self.bot.sleep_till(short_cd)
                
                pool = ["pup", "piku"]
                first = self.bot.random.choice(pool)
                pool.remove(first)
                second = pool[0]

                await self.bot.put_queue(self._build_cmd(first))
                await self.bot.sleep_till([1, 3])
                await self.bot.put_queue(self._build_cmd(second))
                
                await self.bot.sleep(60)
        else:
            if not target_cmd:
                return

            await self.bot.remove_queue(id=target_cmd)
            
            cfg_cooldown = self._cfg(target_cmd).get("cooldown", [300, 400])
            cooldown_val = self.bot.random_float(cfg_cooldown)
            
            if wait_till_next_day:
                cooldown_val += self.bot.calc_time()
                
            await self.bot.sleep(cooldown_val)
            self._mark_sent(target_cmd)
            await self.bot.put_queue(self._build_cmd(target_cmd))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.cm.id:
            return

        if message.author.id == self.bot.user.id:
            content_lower = message.content.lower()
            prefix = self.bot.settings_dict.get("setprefix", "owo ").lower()
            if f"{prefix}pup" in content_lower:
                self._mark_sent("pup")
            if f"{prefix}piku" in content_lower:
                self._mark_sent("piku")
            return

        if message.author.id != self.bot.owo_bot_id:
            return

        detected_cmd = ""
        is_limit = False
        content = message.content

        if "You picked one PikPik carrot" in content:
            detected_cmd = "piku"
        elif "You picked up one puppy" in content:
            detected_cmd = "pup"
            
        if "today!" in content:
            is_limit = True

        if detected_cmd and self._validate_response(detected_cmd):
            self._startup_done = True
            await self._dispatch_cycle(target_cmd=detected_cmd, wait_till_next_day=is_limit)
            return

        detected_cmd = ""
        if "Your garden is out of carrots!" in content:
            detected_cmd = "piku"
            is_limit = True
        elif "There are no puppies to adopt!" in content:
            detected_cmd = "pup"
            is_limit = True

        if detected_cmd and self._validate_response(detected_cmd):
            self._startup_done = True
            await self.bot.log(f"Pupiku: Daily limit reached for {detected_cmd}.", "#e67e22")
            await self._dispatch_cycle(target_cmd=detected_cmd, wait_till_next_day=is_limit)


async def setup(bot):
    await bot.add_cog(PupikuFarmer(bot))
