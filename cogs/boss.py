
from discord.ext import commands
import asyncio
import json
import time
from datetime import datetime, timezone, timedelta
import pytz

from cogs import comp
from discord.ext.commands import ExtensionNotLoaded


class Boss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boss_tickets = 3
        self.sleeping = True
        self.joined_boss_ids = []
        
    def should_join(self, percentage):
        boss_dict = self.bot.settings_dict["bossBattle"]
        random_num = self.bot.random.randint(1, 100)
        return random_num > (100 - boss_dict["joinChancePercent"])

    async def cog_load(self):
        if not self.bot.settings_dict["bossBattle"]["enabled"]:
            try:
                # If disabling boss battle, sometimes people disable daily too? 
                # Original code logic kept here but commmented out if unnecessary
                # asyncio.create_task(self.bot.unload_cog("cogs.daily"))
                pass
            except ExtensionNotLoaded:
                pass
        else:
            await self.bot.log("Boss Battle System Loaded ⚔️", "#ff0000")
            asyncio.create_task(self.time_check())

    async def wait_till_reset_day(self):
        self.sleeping = True
        # Calculate time until midnight PST (OwO reset time)
        # Using simple calculation since bot.calc_time might vary
        pst_timezone = pytz.timezone('US/Pacific') 
        current_time_pst = datetime.now(timezone.utc).astimezone(pst_timezone) 
        midnight_pst = pst_timezone.localize(datetime(current_time_pst.year, current_time_pst.month, current_time_pst.day, 0, 0, 0)) 
        time_until_12am_pst = midnight_pst + timedelta(days=1) - current_time_pst 
        time_to_sleep = time_until_12am_pst.total_seconds()

        await self.bot.log(f"Sleeping boss battle till reset ({int(time_to_sleep)}s)", "#143B02")
        await asyncio.sleep(time_to_sleep)
        await self.time_check()
        self.sleeping = False

    async def time_check(self):
        # TODO: Implement Persistent Database for Boss Tickets
        # For now, we reset to 3 on every restart/reload
        # last_reset_ts, self.boss_tickets = await self.bot.fetch_boss_stats()
        
        self.boss_tickets = 3
        
        # Check if we need to reset based on time (in-memory logic)
        # For now assume fresh start = 3 tickets
        
        # self.bot.update_stats_db("boss", today_midnight_ts)

        self.sleeping = False

    def consume_boss_ticket(self, revert=False):
        if not revert:
            self.boss_tickets -= 1
        else:
            self.boss_tickets += 1
        
        # self.bot.consume_boss_ticket(revert) # TODO DB Sync

    def return_battle_id(self, components):
        for component in components:
            if component.component_name == "media_gallery":
                if component.items and len(component.items) > 0:
                     media_item = component.items[0].media
                     if media_item.url and "reward" in media_item.url:
                        return media_item.placeholder
        return None

    def check_if_joined(self, battle_id):
        if battle_id and battle_id not in self.joined_boss_ids:
            return False
        return True

    @commands.Cog.listener()
    async def on_socket_raw_receive(self, msg):
        """
        Intersept raw socket message to handle Boss components faster/manually
        """
        if self.boss_tickets <= 0 or self.sleeping:
            return

        # Simple check before parsing JSON to save resources
        if '"t":"MESSAGE_CREATE"' not in msg:
            return

        try:
            parsed_msg = json.loads(msg)
            if parsed_msg.get("t") != "MESSAGE_CREATE":
                return
            
            data = parsed_msg.get("d", {})
            
            # Check author is OwO Bot
            if data.get("author", {}).get("id") != str(self.bot.owo_bot_id):
                return

            # Check logic for Join All Guilds
            # channel_id = data.get("channel_id")
            # if not global join enabled and channel_id != self.bot.cm.id: return
            
            # Parse message using our custom component parser
            message = comp.message.get_message_obj(data)

            if message.components:
                for component in message.components:
                    # Boss Embed Detection
                    if component.component_name == "section":
                        # Check content for "runs away" (Boss Battle text)
                        # Structure varies, need to be careful
                        # Usually section -> components -> text
                        
                        found_boss_msg = False
                        if component.components and component.components[0].content:
                             if "runs away" in component.components[0].content:
                                 found_boss_msg = True
                        
                        if found_boss_msg:
                            # Check if battle has already been joined
                            battle_id = self.return_battle_id(message.components)
                            if not battle_id or self.check_if_joined(battle_id):
                                return
                            else:
                                self.joined_boss_ids.append(battle_id)

                            if not self.should_join(self.bot.settings_dict["bossBattle"]["joinChancePercent"]):
                                await self.bot.log("Skipping boss battle (RNG)..", "#6F7C8A")
                                return

                            # Boss Fight button
                            if component.accessory and component.accessory.component_name == "button":
                                if component.accessory.custom_id == "guildboss_fight":
                                    # Fetch guild ID if possible, or use data
                                    # We need guild_id for the interaction
                                    guild_id = data.get("guild_id")
                                    if not guild_id:
                                         # Try fetching channel
                                         try:
                                            ch = self.bot.get_channel(int(message.channel_id))
                                            if ch and ch.guild:
                                                guild_id = ch.guild.id
                                         except:
                                            pass
                                    
                                    if not guild_id:
                                        return

                                    await asyncio.sleep(0.5)
                                    if not self.bot.command_handler_status["captcha"]:
                                        # Click the button using raw request
                                        click_status = await component.accessory.click(
                                            self.bot.ws.session_id, # Access session_id from ws
                                            self.bot.local_headers,
                                            guild_id
                                        )
                                        if click_status:
                                            self.consume_boss_ticket()
                                            await self.bot.log(f"Joined Boss battle! ⚔️ (Tickets left: {self.boss_tickets})", "#B5C1CE")

                    if component.component_name == "text_display":
                        if component.content and "Are you sure you want to use another boss ticket?" in component.content:
                            await self.bot.log("Boss battle was already joined.", "#B5C1CE")
                            self.consume_boss_ticket(revert=True)

                        if component.content and "You don't have any boss tickets!" in component.content:
                            self.boss_tickets = 0
                            self.joined_boss_ids = []
                            # self.bot.reset_boss_ticket(empty=True) 

        except Exception as e:
            # Silently ignore parsing errors to prevent spam
            pass


async def setup(bot):
    await bot.add_cog(Boss(bot))
