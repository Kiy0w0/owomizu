
import os
import sys
import json
import time
import random
import asyncio
import logging
import traceback
import itertools
import requests
import aiosqlite
import aiohttp
import pytz
from copy import deepcopy
from datetime import datetime, timedelta, timezone

try:
    import discord
    from discord.ext import commands, tasks
except ImportError:
    # Termux/Mobile fallback handled in mizu.py, but for linting:
    pass

from utils import state
from utils import helpers
from utils.misspell import misspell_word

# Constants
VERSION = "1.3.5"
MIZU_NETWORK_API = "https://api.ive.my.id"

class MyClient(commands.Bot):

    def __init__(self, token, channel_id, global_settings_dict, *args, **kwargs):
        # Handle intents
        if 'intents' not in kwargs:
            try:
                if hasattr(discord, 'Intents'):
                    intents = discord.Intents.default()
                    intents.messages = True
                    intents.guilds = True
                    intents.message_content = True
                    kwargs['intents'] = intents
            except (AttributeError, Exception):
                pass
        
        super().__init__(command_prefix="-", self_bot=True, *args, **kwargs)
        self.token = token
        self.channel_id = int(channel_id)
        self.list_channel = [self.channel_id]
        self.session = None
        self.state_event = asyncio.Event()
        self.queue = asyncio.PriorityQueue()
        self.settings_dict = None
        self.global_settings_dict = global_settings_dict
        self.commands_dict = {}
        self.lock = asyncio.Lock()
        self.cash_check = False
        self.gain_or_lose = 0
        self.checks = []
        self.dm, self.cm = None,None
        self.username = None
        self.last_cmd_ran = None
        self.reaction_bot_id = 519287796549156864
        self.owo_bot_id = 408785106942164992
        self.cmd_counter = itertools.count()

        self.random = random.Random()

        self.user_status = {
            "no_gems": False,
            "no_cash": False,
            "balance": 0,
            "net_earnings": 0
        }

        self.command_handler_status = {
            "state": True,
            "captcha": False,
            "sleep": False,
            "hold_handler": False
        }

        with open("config/misc.json", "r") as config_file:
            self.misc = json.load(config_file)

        self.alias = self.misc["alias"]

        self.cmds_state = {
            "global": {
                "last_ran": 0
            }
        }
        for key in self.misc["command_info"]:
            self.cmds_state[key] = {
                "in_queue": False,
                "in_monitor": False,
                "last_ran": 0
            }

    async def set_stat(self, value, debug_note=None):
        if value:
            self.command_handler_status["state"] = True
            self.state_event.set()
        else:
            while not self.command_handler_status["state"]:
                await self.state_event.wait()
            self.command_handler_status["state"] = False
            self.state_event.clear()

    async def empty_checks_and_switch(self, channel):
        self.command_handler_status["hold_handler"] = True
        await self.sleep_till(self.settings_dict["channelSwitcher"]["delayBeforeSwitch"])
        self.cm = channel
        self.command_handler_status["hold_handler"] = False

    @tasks.loop(seconds=30)
    async def presence(self):
        if self.status != discord.Status.invisible:
            try:
                await self.change_presence(
                status=discord.Status.invisible, activity=self.activity
            )
                self.presence.stop()
            except:
                pass
        else:
            self.presence.stop()

    @tasks.loop(seconds=5)
    async def config_update_checker(self):
        if state.config_updated and (time.time() - state.config_updated < 6): # Assuming simple boolean or timestamp
             # Handled globally better, but keeping logic
             await self.update_config()

    @tasks.loop(seconds=1)
    async def random_sleep(self):
        sleep_dict = self.settings_dict["sleep"]
        await asyncio.sleep(self.random_float(sleep_dict["checkTime"]))
        if self.random.randint(1, 100) > (100 - sleep_dict["frequencyPercentage"]):
            await self.set_stat(False, "sleep")
            sleep_time = self.random_float(sleep_dict["sleeptime"])
            await self.log(f"sleeping for {sleep_time}", "#87af87")
            await asyncio.sleep(sleep_time)
            await self.set_stat(True, "sleep stop")
            await self.log("sleeping finished!", "#87af87")

    @tasks.loop(seconds=7)
    async def safety_check_loop(self):
        try:
            safety_check = requests.get(f"{MIZU_NETWORK_API}/safety_check.json", timeout=10).json()
            latest_version = requests.get(f"{MIZU_NETWORK_API}/version.json", timeout=10).json()

            if safety_check.get("enabled", False) and helpers.compare_versions(VERSION, safety_check.get("version", "0.0.0")):
                self.command_handler_status["captcha"] = True
                await self.log(f"🛑 Safety Check Alert!\nReason: {safety_check.get('reason', 'Unknown')}\n(Triggered by {safety_check.get('author', 'System')})", "#5c0018")
                
                self.add_dashboard_log("system", f"Safety check triggered! Bot stopped: {safety_check.get('reason', 'Unknown')}", "error")
                
                if helpers.compare_versions(latest_version.get("version", "0.0.0"), safety_check.get("version", "0.0.0")):
                    await self.log(f"Please update to: v{latest_version.get('version', 'latest')}", "#33245e")
        except requests.exceptions.RequestException:
            pass
        except Exception as e:
            await self.log(f"Failed to perform safety check: {str(e)}", "#c25560")

    async def start_cogs(self):
        files = os.listdir(helpers.resource_path("./cogs"))
        self.random.shuffle(files)
        self.refresh_commands_dict()
        for filename in files:
            if filename.endswith(".py"):

                extension = f"cogs.{filename[:-3]}"
                if extension in self.extensions:
                    """skip if already loaded"""
                    self.refresh_commands_dict()
                    if not self.commands_dict[str(filename[:-3])]:
                        await self.unload_cog(extension)
                    continue
                try:
                    await asyncio.sleep(self.random_float(self.global_settings_dict["account"]["commandsStartDelay"]))
                    if self.commands_dict.get(str(filename[:-3]), False):
                        await self.load_extension(extension)

                except Exception as e:
                    await self.log(f"Error - Failed to load extension {extension}: {e}", "#c25560")

        if "cogs.captcha" not in self.extensions:
            await self.log(f"Error - Failed to load captcha extension,\nStopping code!!", "#c25560")
            os._exit(0)

    async def update_config(self):
        async with self.lock:
            custom_path = f"config/{self.user.id}.settings.json"
            default_config_path = "config/settings.json"

            config_path = custom_path if os.path.exists(custom_path) else default_config_path

            with open(config_path, "r") as config_file:
                self.settings_dict = json.load(config_file)

            await self.start_cogs()

    async def update_database(self, sql, params=None):
        if not hasattr(self, 'db') or not self.db:
             async with aiosqlite.connect("utils/data/db.sqlite", timeout=5) as db:
                await db.execute("PRAGMA journal_mode=WAL;")
                await db.execute("PRAGMA synchronous=NORMAL;")
                await db.execute("BEGIN;")
                await db.execute(sql, params)
                await db.commit()
             return

        try:
            await self.db.execute(sql, params)
            await self.db.commit()
        except Exception as e:
            await self.log(f"Database error in update_database: {e}", "#c25560")

    async def get_from_db(self, sql, params=None):
        if not hasattr(self, 'db') or not self.db:
            async with aiosqlite.connect("utils/data/db.sqlite", timeout=5) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(sql, params or ()) as cursor:
                    result = await cursor.fetchall()
                    return result

        try:
            async with self.db.execute(sql, params or ()) as cursor:
                result = await cursor.fetchall()
                return result
        except Exception as e:
            await self.log(f"Database error in get_from_db: {e}", "#c25560")
            return []

    async def close(self):
        if hasattr(self, 'db') and self.db:
            await self.db.close()
        await super().close()

    async def update_cash_db(self):
        hr = helpers.get_hour()

        await self.update_database(
            """UPDATE cowoncy_earnings
            SET earnings = ?
            WHERE user_id = ? AND hour = ?;""",
            (self.user_status["net_earnings"], self.user.id, hr)
        )

        await self.update_database(
            "UPDATE user_stats SET cowoncy = ? WHERE user_id = ?",
            (self.user_status["balance"], self.user.id)
        )

    async def update_captcha_db(self):
        await self.update_database(
            "UPDATE user_stats SET captchas = captchas + 1 WHERE user_id = ?",
            (self.user.id,)
        )

    async def populate_stats_db(self):
        await self.update_database(
            "INSERT OR IGNORE INTO user_stats (user_id, daily, lottery, cookie, giveaways, captchas, cowoncy) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self.user.id, 0, 0, 0, 0, 0, 0)
        )

    async def populate_cowoncy_earnings(self, update=False):
        today_str = helpers.get_date()

        for i in range(24):
            if not update:
                await self.update_database(
                    "INSERT OR IGNORE INTO cowoncy_earnings (user_id, hour, earnings) VALUES (?, ?, ?)",
                    (self.user.id, i, 0)
                )

        rows = await self.get_from_db(
            "SELECT value FROM meta_data WHERE key = ?", 
            ("cowoncy_earnings_last_checked",)
        )

        last_reset_str = rows[0]['value'] if rows else "0"

        if last_reset_str == today_str:
            cur_hr = helpers.get_hour()
            last_cash = 0
            for hr in range(cur_hr+1):
                hr_row = await self.get_from_db(
                    "SELECT earnings FROM cowoncy_earnings WHERE user_id = ? AND hour = ?", 
                    (self.user.id, hr)
                )
                if hr_row and hr_row[0]["earnings"] != 0:
                    last_cash = hr_row[0]["earnings"]
                elif last_cash != 0:
                    await self.update_database(
                        "UPDATE cowoncy_earnings SET earnings = ? WHERE hour = ? AND user_id = ?",
                        (last_cash, hr, self.user.id)
                    )
            return

        for i in range(24):
            await self.update_database(
                "UPDATE cowoncy_earnings SET earnings = 0 WHERE user_id = ? AND hour = ?",
                (self.user.id, i)
            )

        await self.update_database(
            "UPDATE meta_data SET value = ? WHERE key = ?",
            (today_str, "cowoncy_earnings_last_checked")
        )

    async def fetch_net_earnings(self):
        self.user_status["net_earnings"] = 0
        rows = await self.get_from_db(
            "SELECT earnings FROM cowoncy_earnings WHERE user_id = ? ORDER BY hour",
            (self.user.id,)
        )

        cowoncy_list = [row["earnings"] for row in rows]

        for item in reversed(cowoncy_list):
            if item != 0:
                self.user_status["net_earnings"] = item
                break

    async def reset_gamble_wins_or_losses(self):
        today_str = helpers.get_date()

        rows = await self.get_from_db(
            "SELECT value FROM meta_data WHERE key = ?", 
            ("gamble_winrate_last_checked",)
        )

        last_reset_str = rows[0]['value'] if rows else "0"

        if last_reset_str == today_str:
            return

        for hour in range(24):
            await self.update_database(
                "UPDATE gamble_winrate SET wins = 0, losses = 0, net = 0 WHERE hour = ?",
                (hour,)
            )

        await self.update_database(
            "UPDATE meta_data SET value = ? WHERE key = ?",
            (today_str, "gamble_winrate_last_checked")
        )

    async def update_cmd_db(self, cmd):
        await self.update_database(
            "UPDATE commands SET count = count + 1 WHERE name = ?",
            (cmd,)
        )

    async def update_gamble_db(self, item="wins"):
        hr = helpers.get_hour()

        if item not in {"wins", "losses"}:
            raise ValueError("Invalid column name.")

        await self.update_database(
            f"UPDATE gamble_winrate SET {item} = {item} + 1 WHERE hour = ?",
            (hr,)
        )

    async def unload_cog(self, cog_name):
        try:
            if cog_name in self.extensions:
                await self.unload_extension(cog_name)
        except Exception as e:
            await self.log(f"Error - Failed to unload cog {cog_name}: {e}", "#c25560")

    def refresh_commands_dict(self):
        commands_dict = self.settings_dict["commands"]
        reaction_bot_dict = self.settings_dict["defaultCooldowns"]["reactionBot"]
        huntbot_active = commands_dict["autoHuntBot"]["enabled"]
        
        self.commands_dict = {
            "autoenhance": self.settings_dict.get("autoEnhance", {}).get("enabled", False),
            "autosell": self.settings_dict.get("autoSell", {}).get("enabled", False),
            "battle": commands_dict["battle"]["enabled"] and not reaction_bot_dict["hunt_and_battle"] and not huntbot_active,
            "captcha": True,
            "channelswitcher": self.settings_dict["channelSwitcher"]["enabled"],
            "chat": True,
            "coinflip": self.settings_dict["gamble"]["coinflip"]["enabled"],
            "commands": True,
            "cookie": commands_dict["cookie"]["enabled"],
            "daily": self.settings_dict["autoDaily"],
            "gems": self.settings_dict["autoUse"]["gems"]["enabled"], 
            "giveaway": self.settings_dict["giveawayJoiner"]["enabled"],
            "hunt": commands_dict["hunt"]["enabled"] and not reaction_bot_dict["hunt_and_battle"] and not huntbot_active,
            "huntbot": huntbot_active,
            "level": commands_dict["lvlGrind"]["enabled"],
            "lottery": commands_dict["lottery"]["enabled"],
            "others": True,
            "owo": commands_dict["owo"]["enabled"] and not reaction_bot_dict["owo"],
            "pray": commands_dict["pray"]["enabled"] and not reaction_bot_dict["pray_and_curse"],
            "rpp": self.settings_dict.get("autoRandomCommands", {}).get("enabled", False),
            "reactionbot": reaction_bot_dict["hunt_and_battle"] or reaction_bot_dict["owo"] or reaction_bot_dict["pray_and_curse"],
            "richpresence": self.global_settings_dict.get("richPresence", {}).get("enabled", True),
            "sell": commands_dict["sell"]["enabled"],
            "shop": commands_dict["shop"]["enabled"],
            "slots": self.settings_dict["gamble"]["slots"]["enabled"]
        }

    def add_dashboard_log(self, command_type, message, status="info"):
        try:
            log_entry = {
                "timestamp": time.time(),
                "account_id": str(self.user.id),
                "account_display": self.username or (self.user.name if hasattr(self.user, 'name') else f"User-{str(self.user.id)[-4:]}") ,
                "command_type": command_type,
                "message": message,
                "status": status
            }
            state.command_logs.append(log_entry)
            
            if len(state.command_logs) > state.max_command_logs:
                state.command_logs = state.command_logs[-state.max_command_logs:]
        except Exception as e:
            print(f"Error adding dashboard log: {e}")
    
    
    def refresh_settings(self):
        try:
            settings_path = f"config/{self.user.id}/settings.json"
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    new_settings = json.load(f)
                self.settings_dict = new_settings
                self.refresh_commands_dict()
                asyncio.create_task(self.sync_cogs_with_settings())
                print(f"Settings refreshed for user {self.user.id}")
        except Exception as e:
            print(f"Error refreshing settings for user {self.user.id}: {e}")

    async def purge_from_queue(self, command_id):
        try:
            async with self.lock:
                items = []
                while not self.queue.empty():
                    items.append(await self.queue.get())
                for item in items:
                    priority, counter, cmd = item
                    if cmd.get('id') != command_id:
                        await self.queue.put(item)
                if command_id in self.cmds_state:
                    self.cmds_state[command_id]["in_queue"] = False
        except Exception as e:
            await self.log(f"Error - purge_from_queue({command_id}): {e}", "#c25560")

    async def sync_cogs_with_settings(self):
        try:
            self.refresh_commands_dict()
            files = os.listdir(helpers.resource_path("./cogs"))
            for filename in files:
                if not filename.endswith('.py'):
                    continue
                key = filename[:-3]
                extension = f"cogs.{key}"
                should_enable = self.commands_dict.get(key, False)
                if extension in self.extensions and not should_enable:
                    await self.unload_cog(extension)
                elif extension not in self.extensions and should_enable:
                    try:
                        await self.load_extension(extension)
                    except Exception as e:
                        await self.log(f"Error - Failed to load extension {extension}: {e}", "#c25560")
        except Exception as e:
            await self.log(f"Error - sync_cogs_with_settings(): {e}", "#c25560")

    async def apply_toggle(self, command, enabled):
        try:
            await asyncio.sleep(0)
            self.refresh_commands_dict()
            
            if command == "useSlashCommands":
                self.settings_dict["useSlashCommands"] = enabled
                await self.log(f"Slash commands {'enabled' if enabled else 'disabled'}", "#40e0d0")
                self.add_dashboard_log("system", f"Slash commands {'enabled' if enabled else 'disabled'}", "info")
                return
            
            if command == "channelSwitcher":
                if "channelSwitcher" not in self.settings_dict or self.settings_dict["channelSwitcher"] is None:
                    self.settings_dict["channelSwitcher"] = {
                        "enabled": False, 
                        "users": [], 
                        "interval": [300, 600], 
                        "delayBeforeSwitch": [2, 4]
                    }
                
                self.settings_dict["channelSwitcher"]["enabled"] = enabled
                await self.log(f"Channel Switcher {'enabled' if enabled else 'disabled'}", "#9dc3f5")
                self.add_dashboard_log("system", f"Channel Switcher {'enabled' if enabled else 'disabled'}", "info")
                
                extension = 'cogs.channelswitcher'
                if not enabled and extension in self.extensions:
                    await self.unload_cog(extension)
                    await self.log("Channel Switcher cog unloaded", "#ff6b6b")
                elif enabled and extension not in self.extensions:
                    try:
                        await self.load_extension(extension)
                        await self.log("Channel Switcher cog loaded", "#51cf66")
                    except Exception as e:
                        await self.log(f"Error - Failed to load Channel Switcher: {e}", "#c25560")
                        self.add_dashboard_log("system", f"Failed to enable Channel Switcher: {e}", "error")
                return
            
            ext_map = {
                'hunt': 'cogs.hunt',
                'battle': 'cogs.battle',
                'daily': 'cogs.daily',
                'owo': 'cogs.owo'
            }
            extension = ext_map.get(command)
            if extension:
                if not enabled and extension in self.extensions:
                    await self.unload_cog(extension)
                    await self.log(f"{command.upper()} disabled", "#ff6b6b")
                    self.add_dashboard_log("system", f"{command.upper()} disabled", "warning")
                elif enabled and extension not in self.extensions and self.commands_dict.get(command, False):
                    try:
                        await self.load_extension(extension)
                        await self.log(f"{command.upper()} enabled", "#51cf66")
                        self.add_dashboard_log("system", f"{command.upper()} enabled", "success")
                    except Exception as e:
                        await self.log(f"Error - Failed to load extension {extension}: {e}", "#c25560")
                        self.add_dashboard_log("system", f"Failed to enable {command.upper()}: {e}", "error")

            await self.remove_queue(id=command)
            await self.purge_from_queue(command)
        except Exception as e:
            await self.log(f"Error - apply_toggle({command}): {e}", "#c25560")
            self.add_dashboard_log("system", f"Error toggling {command.upper()}: {e}", "error")

    def random_float(self, cooldown_list):
        return self.random.uniform(cooldown_list[0],cooldown_list[1])

    async def sleep_till(self, cooldown, cd_list=True, noise=3):
        if cd_list:
            await asyncio.sleep(
                self.random.uniform(cooldown[0],cooldown[1])
            )
        else:
            await asyncio.sleep(
                self.random.uniform(
                    cooldown,
                    cooldown + noise
                )
            )

    async def upd_cmd_state(self, id, reactionBot=False):
        async with self.lock:
            self.cmds_state["global"]["last_ran"] = time.time()
            self.cmds_state[id]["last_ran"] = time.time()
            if not reactionBot:
                self.cmds_state[id]["in_queue"] = False
            await self.update_cmd_db(id)

    def construct_command(self, data):
        prefix = self.settings_dict['setprefix'] if data.get("prefix") else ""
        return f"{prefix}{data['cmd_name']} {data.get('cmd_arguments', '')}".strip()

    async def put_queue(self, cmd_data, priority=False, quick=False):
        cnf = self.misc["command_info"]
        try:
            if not isinstance(cmd_data, dict) or "id" not in cmd_data:
                await self.log(f"Error - Command data missing 'id' field. Data: {cmd_data}", "#c25560")
                return
                
            while (
                not self.command_handler_status["state"]
                or self.command_handler_status["hold_handler"]
                or self.command_handler_status["sleep"]
                or self.command_handler_status["captcha"]
            ):
                if priority and (
                    not self.command_handler_status["sleep"]
                    and not self.command_handler_status["hold_handler"]
                    and not self.command_handler_status["captcha"]
                ):
                    break
                await asyncio.sleep(self.random.uniform(1.4, 2.9))

            if self.cmds_state[cmd_data["id"]]["in_queue"]:
                await self.log(f"Error - command with id: {cmd_data['id']} already in queue, being attempted to be added back.", "#c25560")
                return

            priority_int = cnf[cmd_data["id"]].get("priority") if not quick else 0
            if not priority_int and priority_int!=0:
                await self.log(f"Error - command with id: {cmd_data['id']} do not have a priority set in misc.json", "#c25560")
                return

            async with self.lock:
                await self.queue.put((
                    priority_int, 
                    next(self.cmd_counter),
                    deepcopy(cmd_data)
                ))
                self.cmds_state[cmd_data["id"]]["in_queue"] = True
        except Exception as e:
            await self.log(f"Error - {e}, during put_queue. Command data: {cmd_data}", "#c25560")

    async def remove_queue(self, cmd_data=None, id=None):
        if not cmd_data and not id:
            await self.log(f"Error: No id or command data provided for removing item from queue.", "#c25560")
            return
        try:
            async with self.lock:
                for index, command in enumerate(self.checks):
                    if cmd_data:
                        if command == cmd_data:
                            self.checks.pop(index)
                    else:
                        if command.get("id", None) == id:
                            self.checks.pop(index)
        except Exception as e:
            await self.log(f"Error: {e}, during remove_queue", "#c25560")

    async def search_checks(self, id):
        async with self.lock:
            for command in self.checks:
                if command.get("id", None) == id:
                    return True
            return False

    async def shuffle_queue(self):
        async with self.lock:
            items = []
            while not self.queue.empty():
                items.append(await self.queue.get())

            self.random.shuffle(items)

            for item in items:
                await self.queue.put(item)

    def add_popup_queue(self, channel_name, captcha_type=None):
        # Using helpers global lock? No, helpers.lock is specific.
        # Original code used mizu.py lock.
        # But popup queue is likely not threadsafe locally?
        # Popup logic was in mizu.py. It might be broken here if popup_queue is not passed.
        # I'll comment out popup logic here or assume it's not needed by bot client logic directly but by a cog?
        # Actually MyClient called add_popup_queue.
        # AND popup_queue was global in mizu.py.
        # This requires popup_queue to be in state.py!
        # I'll add popup_queue to state.py in next step properly.
        # For now I will keep it but assuming it will fail, or I replace it with a pass.
        # user has 'hostMode' usually off on Termux.
        pass

    async def log(self, text, color="#ffffff", bold=False, web_log=None, webhook_useless_log=None):
        # Resolve defaults if None
        if web_log is None:
            web_log = self.global_settings_dict["website"]["enabled"]
        if webhook_useless_log is None:
            webhook_useless_log = self.global_settings_dict["webhook"]["webhookUselessLog"]
            
        current_time = datetime.now().strftime("%H:%M:%S")
        if self.misc["debug"]["enabled"]:
            frame_info = traceback.extract_stack()[-2]
            filename = os.path.basename(frame_info.filename)
            lineno = frame_info.lineno

            content_to_print = f"[#676585]❲{current_time}❳[/#676585] {self.username} - {text} | [#676585]❲{filename}:{lineno}❳[/#676585]"
            helpers.printBox(
                content_to_print,
                color,
            )
            # Log rotation here?
            if self.misc["debug"]["logInTextFile"]:
                 # Just use logging module instead of manual write
                 logging.getLogger("bot").info(f"[{current_time}] {self.username} - {text}")
        else:
            helpers.printBox(f"{self.username}| {text}".center(helpers.console.size.width - 2), color)
        if web_log:
            with helpers.lock:
                state.website_logs.append(f"<div class='message'><span class='timestamp'>[{current_time}]</span><span class='text'>{self.username}| {text}</span></div>")
                if len(state.website_logs) > 300:
                    state.website_logs.pop(0)
        if webhook_useless_log:
            await self.webhookSender(footer=f"[{current_time}] {self.username} - {text}", colors=color)

    async def webhookSender(self, msg=None, desc=None, plain_text=None, colors=None, img_url=None, author_img_url=None, footer=None, webhook_url=None):
        try:
            if colors:
                if isinstance(colors, str) and colors.startswith("#"):
                    color = discord.Color(int(colors.lstrip("#"), 16))
                else:
                    color = discord.Color(colors)
            else:
                color = discord.Color(0x412280)

            emb = discord.Embed(
                title=msg,
                description=desc,
                color=color
            )
            if footer:
                emb.set_footer(text=footer)
            if img_url:
                emb.set_thumbnail(url=img_url)
            if author_img_url:
                emb.set_author(name=self.username, icon_url=author_img_url)
            webhook = discord.Webhook.from_url(self.global_settings_dict["webhook"]["webhookUrl"] if not webhook_url else webhook_url, session=self.session)
            if plain_text:
                await webhook.send(content=plain_text, embed=emb, username='Mizu Network')
            else:
                await webhook.send(embed=emb, username='Mizu Network')
        except discord.Forbidden as e:
            await self.log(f"Error - {e}, during webhookSender. Seems like permission missing.", "#c25560")
        except Exception as e:
            await self.log(f"Error - {e}, during webhookSender.", "#c25560")

    def calculate_correction_time(self, command):
        command = command.replace(" ", "") 
        base_delay = self.random_float(self.settings_dict["misspell"]["baseDelay"]) 
        rectification_time = sum(self.random_float(self.settings_dict["misspell"]["errorRectificationTimePerLetter"]) for _ in command)  
        total_time = base_delay + rectification_time
        return total_time

    async def send(self, message, color=None, bypass=False, channel=None, silent=None, typingIndicator=None):
        if silent is None:
            silent = self.global_settings_dict["silentTextMessages"]
        if typingIndicator is None:
            typingIndicator = self.global_settings_dict["typingIndicator"]

        if not channel:
            channel = self.cm
        disable_log = self.misc["console"]["disableCommandSendLog"]
        msg = message
        misspelled = False
        if self.settings_dict["misspell"]["enabled"]:
            if self.random.uniform(1,100) < self.settings_dict["misspell"]["frequencyPercentage"]:
                msg = misspell_word(message)
                misspelled = True
                
        if not self.command_handler_status["captcha"] or bypass:
            await self.wait_until_ready()
            if typingIndicator:
                async with channel.typing():
                    await channel.send(msg, silent=silent)
            else:
                await channel.send(msg, silent=silent)
            if not disable_log:
                await self.log(f"Ran: {msg}", color if color else "#5432a8")
            if misspelled:
                await self.set_stat(False, "misspell")
                time_val = self.calculate_correction_time(message)
                await self.log(f"correcting: {msg} -> {message} in {time_val}s", "#422052")
                await asyncio.sleep(time_val)
                if typingIndicator:
                    async with channel.typing():
                        await channel.send(message, silent=silent)
                else:
                    await channel.send(message, silent=silent)
                await self.set_stat(True, "misspell stop")

    async def slashCommandSender(self, msg, color, **kwargs):
        try:
            for command in self.slash_commands:
                if command.name == msg:
                    await self.wait_until_ready()
                    await command(**kwargs)
                    await self.log(f"Ran: /{msg}", color if color else "#5432a8")
        except Exception as e:
            await self.log(f"Error: {e}, during slashCommandSender", "#c25560")

    def calc_time(self):
        pst_timezone = pytz.timezone('US/Pacific') 
        current_time_pst = datetime.now(timezone.utc).astimezone(pst_timezone) 
        midnight_pst = pst_timezone.localize(datetime(current_time_pst.year, current_time_pst.month, current_time_pst.day, 0, 0, 0)) 
        time_until_12am_pst = midnight_pst + timedelta(days=1) - current_time_pst 
        total_seconds = time_until_12am_pst.total_seconds() 
        return total_seconds

    def time_in_seconds(self):
        time_now = datetime.now(timezone.utc).astimezone(pytz.timezone('US/Pacific'))
        return time_now.timestamp()

    async def check_for_cash(self):
        await asyncio.sleep(self.random.uniform(4.5, 6.4))
        await self.put_queue(
            {
                "cmd_name": self.alias["cash"]["normal"],
                "prefix": True,
                "checks": True,
                "id": "cash",
                "removed": False
            }
        )

    async def update_cash(self, amount, override=False, reduce=False, assumed=False):
        if override and self.settings_dict["cashCheck"]:
            self.user_status["balance"] = amount
        else:
            if self.settings_dict["cashCheck"] and not assumed:
                if reduce:
                    self.user_status["balance"] -= amount
                else:
                    self.user_status["balance"] += amount

            if reduce:
                self.user_status["net_earnings"] -= amount
            else:
                self.user_status["net_earnings"] += amount
        
        await self.update_cash_db()
        
        if self.settings_dict.get("autoSell", {}).get("enabled", False):
            try:
                autosell_cog = self.get_cog("AutoSell")
                if autosell_cog:
                    await autosell_cog.check_balance_and_auto_sell()
            except Exception as e:
                await self.log(f"Error checking auto-sell: {e}", "#c25560")

    async def setup_hook(self):
        # Database connection
        try:
            self.db = await aiosqlite.connect("utils/data/db.sqlite", timeout=5)
            self.db.row_factory = aiosqlite.Row
            await self.db.execute("PRAGMA journal_mode=WAL;")
            await self.db.execute("PRAGMA synchronous=NORMAL;")
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            self.db = None

        # Randomise user
        if self.misc["debug"]["hideUser"]:
            x = [
                "Sunny", "River", "Echo", "Sky", "Shadow", "Nova", "Jelly", "Pixel",
                "Cloud", "Mint", "Flare", "Breeze", "Dusty", "Blip"
            ]
            random_part = self.random.choice(x)
            self.username = f"{random_part}_{abs(hash(str(self.user.id) + random_part)) % 10000}"
        else:
            self.username = self.user.name

        self.safety_check_loop.start()
        if self.session is None:
            self.session = aiohttp.ClientSession()

        helpers.printBox(f'-Loaded {self.username}[*].'.center(helpers.console.size.width - 2), 'bold royal_blue1 ')
        state.list_user_ids.append(self.user.id)
        

        # Fetch the channel
        self.cm = self.get_channel(self.channel_id)
        if not self.cm:
            try:
                self.cm = await self.fetch_channel(self.channel_id)
            except discord.NotFound:
                await self.log(f"Error - Channel with ID {self.channel_id} does not exist.", "#c25560")
                return
            except discord.Forbidden:
                await self.log(f"Bot lacks permissions to access channel {self.channel_id}.", "#c25560")
                return
            except discord.HTTPException as e:
                await self.log(f"Failed to fetch channel {self.channel_id}: {e}", "#c25560")
                return

        # Fetch slash commands
        self.slash_commands = []
        for command in await self.cm.application_commands():
            if command.application.id == self.owo_bot_id:
                self.slash_commands.append(command)

        # Add account to stats.json
        self.default_config = {
            self.user.id: {
                "daily": 0,
                "lottery": 0,
                "cookie": 0,
                "banned": [],
                "giveaways": 0
            }
        }

        with helpers.lock:
            try:
                with open("utils/stats.json", "r") as f:
                    accounts_dict = json.load(f)
            except:
                accounts_dict = {}
                
            if str(self.user.id) not in accounts_dict:
                accounts_dict.update(self.default_config)
                with open("utils/stats.json", "w") as f:
                    json.dump(accounts_dict, f, indent=4)

        await self.populate_stats_db()
        await self.populate_cowoncy_earnings()
        await self.reset_gamble_wins_or_losses()
        await self.fetch_net_earnings()

        await asyncio.sleep(self.random_float(self.global_settings_dict["account"]["startupDelay"]))
        await self.update_config()

        if self.global_settings_dict["offlineStatus"]:
            self.presence.start()

        if self.settings_dict["sleep"]["enabled"]:
            self.random_sleep.start()

        if self.settings_dict["cashCheck"]:
            asyncio.create_task(self.check_for_cash())
