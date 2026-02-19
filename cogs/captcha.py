"""
Mizu OwO Bot - Captcha Handler & Auto-Solver
Copyright (C) 2026 MizuNetwork
Copyright (C) 2026 Kiy0w0

Part of the OwOMizu Project (https://github.com/Kiy0w0/owomizu)
Auto-Solver powered by Aurabeam Captcha Solver (https://github.com/Kiy0w0/aurabeam-captcha-solver)
"""

import threading
import time
import re
import os
import asyncio
import tempfile

from discord.ext import commands, tasks
from discord import DMChannel

# Captcha Solver (Optional - requires ddddocr & opencv)
SOLVER_AVAILABLE = False
MAX_SOLVE_STRATEGIES = 0
try:
    from captcha_solver.solve import solve_captcha, get_strategy_count
    SOLVER_AVAILABLE = True
    MAX_SOLVE_STRATEGIES = get_strategy_count()
except ImportError:
    pass

list_captcha = ["human", "captcha", "link", "letterword"]

# OwO bot responses indicating wrong captcha answer
WRONG_ANSWER_PHRASES = [
    "wrong answer",
    "incorrect",
    "that is not right",
    "try again",
    "wrong! you have",
]

def get_path(path):
    cur_dir = os.getcwd()
    if os.path.isfile(path):
        """See if complete path"""
        return path
    audio_folder_path = os.path.join(cur_dir, "audio", path)
    if os.path.isfile(audio_folder_path):
        """See if audio file is in audio folder"""
        return audio_folder_path
    file_in_cwd = os.path.join(cur_dir, path)
    if os.path.isfile(file_in_cwd):
        """See if audio file is in working directory"""
        return file_in_cwd
    """None otherwise"""
    return None



def clean(msg):
    return re.sub(r"[^a-zA-Z]", "", msg)

def is_termux():
    termux_prefix = os.environ.get("PREFIX")
    termux_home = os.environ.get("HOME")
    
    if termux_prefix and "com.termux" in termux_prefix:
        return True
    elif termux_home and "com.termux" in termux_home:
        return True
    else:
        return os.path.isdir("/data/data/com.termux")

on_mobile = is_termux()

if not on_mobile:
    #desktop
    from plyer import notification
    from playsound3 import playsound


def run_system_command(command, timeout, retry=False, delay=5):
    def target():
        try:
            os.system(command)
        except Exception as e:
            print(f"Error executing command: {command} - {e}")

    # Create and start a thread to execute the command
    thread = threading.Thread(target=target)
    thread.start()

    # Wait for the thread to finish, with a timeout
    thread.join(timeout)

    # If the thread is still alive after the timeout, terminate it
    if thread.is_alive():
        print(f"Error: {command} command failed! (captcha)")
        if retry:
            print(f"Retrying '{command}' after {delay}s")
            time.sleep(delay)
            run_system_command(command, timeout)

def get_channel_name(channel):
    if isinstance(channel, DMChannel):
        return "owo DMs"
    return channel.name

def console_handler(cnf, captcha=True):
    if cnf["runConsoleCommandOnCaptcha"] and captcha:
        run_system_command(cnf["commandToRunOnCaptcha"], timeout=5)
    elif cnf["runConsoleCommandOnBan"] and not captcha:
        run_system_command(cnf["commandToRunOnBan"], timeout=5)


class Captcha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Retry state for auto-solver
        self._solve_attempt = 0          # Current strategy index
        self._solve_max_retries = 3      # Max retries (strategies 0,1,2,3)
        self._captcha_image_path = None  # Saved image path for retries
        self._captcha_channel = None     # Channel to send answer to
        self._solving_active = False     # Whether we're in a solve cycle

    async def _download_image(self, url):
        """Download an image from URL and return bytes"""
        try:
            async with self.bot.session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
        except Exception as e:
            await self.bot.log(f"Failed to download captcha image: {e}", "#c25560")
        return None

    async def _attempt_solve(self, strategy_index=0):
        """Attempt to solve the cached captcha image with a specific strategy."""
        if not self._captcha_image_path or not os.path.exists(self._captcha_image_path):
            await self.bot.log("🧩 Auto-Solver: No cached captcha image to solve", "#c25560")
            return False

        try:
            strategy_names = ["Standard", "Adaptive", "Heavy Distortion", "OTSU Auto"]
            name = strategy_names[strategy_index] if strategy_index < len(strategy_names) else f"Strategy {strategy_index}"
            
            await self.bot.log(f"🧩 Auto-Solver: Attempt {strategy_index + 1}/{self._solve_max_retries + 1} using [{name}]...", "#f39c12")
            self.bot.add_dashboard_log("captcha", f"Auto-Solver attempt {strategy_index + 1} [{name}]", "warning")

            # Run solver in executor (blocking call)
            loop = asyncio.get_event_loop()
            answer = await loop.run_in_executor(None, solve_captcha, self._captcha_image_path, strategy_index)

            if answer and len(answer) > 0:
                await self.bot.log(f"🧩 Auto-Solver result: '{answer}' [{name}]", "#51cf66")
                self.bot.add_dashboard_log("captcha", f"Auto-Solver answer: {answer} [{name}]", "success")

                # Human-like delay before answering
                delay = self.bot.random_float([2.0, 5.0])
                await asyncio.sleep(delay)

                # Send answer
                if self._captcha_channel:
                    await self._captcha_channel.send(answer)
                    await self.bot.log(f"🧩 Auto-Solver: Sent '{answer}' to {get_channel_name(self._captcha_channel)}", "#51cf66")
                    return True
            else:
                await self.bot.log(f"🧩 Auto-Solver: Empty result from [{name}]", "#c25560")
        except Exception as e:
            await self.bot.log(f"🧩 Auto-Solver error (attempt {strategy_index + 1}): {e}", "#c25560")
        
        return False

    def _cleanup_captcha(self):
        """Cleanup temp captcha image and reset state."""
        if self._captcha_image_path:
            try:
                os.remove(self._captcha_image_path)
            except:
                pass
        self._captcha_image_path = None
        self._captcha_channel = None
        self._solve_attempt = 0
        self._solving_active = False

    def captcha_handler(self, channel, captcha_type):
        if self.bot.misc["hostMode"]:
            return
        cnf = self.bot.global_settings_dict["captcha"]
        channel_name = get_channel_name(channel)
        content = 'captchaContent' if not captcha_type=="Ban" else 'bannedContent'
        """Notifications"""
        if cnf["notifications"]["enabled"]:
            try:
                if on_mobile:
                    run_system_command(
                        f"termux-notification -t '{self.bot.username} captcha!' -c '{cnf['notifications'][content].format(username=self.bot.username,channelname=channel_name,captchatype=captcha_type)}' --led-color '#a575ff' --priority 'high'",
                        timeout=5, 
                        retry=True
                        )
                else:
                    notification.notify(
                        title=f'{self.bot.username} DETECTED CAPTCHA',
                        message=cnf['notifications'][content].format(username=self.bot.username,channelname=channel_name,captchatype=captcha_type),
                        app_icon=None,
                        timeout=15
                        )
            except Exception as e:
                print(f"{e} - at notifs")
                
        """Play audio file"""
        """
        TASK: add two checks, check the path for the file in both outside utils folder
        and in bot folder
        +
        better error handling for missing PATH
        """
        if cnf["playAudio"]["enabled"]:
            path = get_path(cnf['playAudio']['path'])
            try:
                if on_mobile:
                    run_system_command(f"termux-media-player play {path}", timeout=5, retry=True)
                else:
                    playsound(path, block=False)
            except Exception as e:
                print(f"{e} - at audio")
        """Toast/Popup"""
        if cnf["toastOrPopup"]["enabled"]:
            try:
                if on_mobile:
                    run_system_command(
                        f"termux-toast -c {cnf['toastOrPopup']['termuxToast']['textColour']} -b {cnf['toastOrPopup']['termuxToast']['backgroundColour']} -g {cnf['toastOrPopup']['termuxToast']['position']} '{cnf['toastOrPopup'][content].format(username=self.bot.username,channelname=channel_name,captchatype=captcha_type)}'",
                        timeout=5,
                        retry=True
                        )
                else:
                    self.bot.add_popup_queue(channel_name, captcha_type)
            except Exception as e:
                print(f"{e} - at Toast/Popup")
        """Termux - Vibrate"""
        if cnf["termux"]["vibrate"]["enabled"]:
            try:
                if on_mobile:
                    run_system_command(
                        f"termux-vibrate -f -d {cnf['termux']['vibrate']['time']*1000}",
                        timeout=5,
                        retry=True,
                    )
                else:
                    pass
            except Exception as e:
                print(f"{e} - at Toast/Popup")
        """Termux - TTS"""
        if cnf["termux"]["textToSpeech"]["enabled"]:
            try:
                if on_mobile:
                    run_system_command(
                            f"termux-tts-speak {cnf['termux']['textToSpeech'][content]}",
                            timeout=7,
                            retry=False
                        )
                else:
                    pass
            except Exception as e:
                print(f"{e} - at Toast/Popup")
        """Termux - open captcha website"""
        if cnf["termux"]["openCaptchaWebsite"] and on_mobile:
            run_system_command("termux-open https://owobot.com/captcha", timeout=5, retry=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        self.last_msg = time.time()

        if not self.bot.dm:
            if message.author.id == self.bot.owo_bot_id:
                self.bot.dm = await message.author.create_dm()
            else:
                # Safe, since only owobot will send captcha messages.
                return


        if message.channel.id == self.bot.dm.id and message.author.id == self.bot.owo_bot_id:
            if "I have verified that you are human! Thank you! :3" in message.content:
                # Captcha solved successfully!
                self._cleanup_captcha()
                
                time_to_sleep = self.bot.random_float(self.bot.settings_dict['defaultCooldowns']['captchaRestart'])
                await self.bot.log(f"Captcha solved! - sleeping {time_to_sleep}s before restart.", "#5fd700")
                
                # Add dashboard log for captcha solved
                self.bot.add_dashboard_log("captcha", f"Captcha solved! Resuming in {time_to_sleep:.1f}s", "success")
                
                await asyncio.sleep(time_to_sleep)
                self.bot.command_handler_status["captcha"] = False
                
                # Add dashboard log for bot resumed
                self.bot.add_dashboard_log("system", "Bot automatically resumed after captcha", "success")
                await self.bot.log(f"Bot automatically resumed after captcha!", "#51cf66")
                
                await self.bot.update_captcha_db()
                return

            # === WRONG ANSWER RETRY ===
            content_lower = message.content.lower()
            if self._solving_active and any(phrase in content_lower for phrase in WRONG_ANSWER_PHRASES):
                self._solve_attempt += 1
                if self._solve_attempt <= self._solve_max_retries and self._solve_attempt < MAX_SOLVE_STRATEGIES:
                    await self.bot.log(f"🧩 Auto-Solver: Wrong answer! Retrying with strategy {self._solve_attempt + 1}...", "#f39c12")
                    self.bot.add_dashboard_log("captcha", f"Wrong answer - retrying (attempt {self._solve_attempt + 1})", "warning")
                    
                    # Small delay before retry
                    await asyncio.sleep(self.bot.random_float([1.5, 3.0]))
                    await self._attempt_solve(strategy_index=self._solve_attempt)
                else:
                    await self.bot.log(f"🧩 Auto-Solver: All {self._solve_attempt} attempts failed. Manual solve required.", "#d70000")
                    self.bot.add_dashboard_log("captcha", "Auto-Solver exhausted all strategies - manual solve needed", "error")
                    self._cleanup_captcha()
                    self.captcha_handler(self._captcha_channel or message.channel, "Link")
                return

        if message.channel.id in {self.bot.dm.id, self.bot.cm.id} and message.author.id == self.bot.owo_bot_id:
            """Handle normally expected captcha"""
            if (
                (
                    message.components
                    and len(message.components) > 0
                    and hasattr(message.components[0], "children")
                    and len(message.components[0].children) > 0
                    and (
                        (
                            hasattr(message.components[0].children[0], "label")
                            and message.components[0].children[0].label == "Verify"
                        )
                        or (
                            hasattr(message.components[0].children[0], "url")
                            and message.components[0].children[0].url
                            == "https://owobot.com?login="
                        )
                    )
                )
                or (
                    "⚠️" in message.content and message.attachments
                )  # message attachment check
                or any(b in clean(message.content) for b in list_captcha)
            ):
                if not get_channel_name(message.channel) == "owo DMs":
                    display_name = message.guild.me.display_name
                    if not any(user in message.content for user in (self.bot.user.name, f"<@{self.bot.user.id}>", display_name)):
                        return
                self.bot.command_handler_status["captcha"] = True
                await self.bot.log(f"Captcha detected!", "#d70000")
                
                # Add dashboard log for captcha detected
                channel_name = get_channel_name(message.channel)
                self.bot.add_dashboard_log("captcha", f"Captcha detected in {channel_name}! Bot stopped automatically", "error")
                
                # === AUTO-SOLVE WITH RETRY ===
                auto_solved = False
                if SOLVER_AVAILABLE and message.attachments and self.bot.global_settings_dict.get("captcha", {}).get("autoSolve", {}).get("enabled", False):
                    try:
                        await self.bot.log("🧩 Auto-Solver: Captcha image detected, starting solve cycle...", "#f39c12")
                        
                        # Download image to temp file (keep for retries)
                        img_url = message.attachments[0].url
                        img_data = await self._download_image(img_url)
                        
                        if img_data:
                            # Save for retry access
                            tmp_path = os.path.join(tempfile.gettempdir(), f"mizu_captcha_{self.bot.user.id}.png")
                            with open(tmp_path, "wb") as f:
                                f.write(img_data)
                            
                            # Setup retry state
                            self._captcha_image_path = tmp_path
                            self._captcha_channel = message.channel
                            self._solve_attempt = 0
                            self._solving_active = True
                            
                            # First attempt (strategy 0)
                            auto_solved = await self._attempt_solve(strategy_index=0)
                        else:
                            await self.bot.log("🧩 Auto-Solver: Failed to download captcha image", "#c25560")
                    except Exception as e:
                        await self.bot.log(f"🧩 Auto-Solver error: {e}", "#c25560")
                        self.bot.add_dashboard_log("captcha", f"Auto-Solver error: {e}", "error")
                # === END AUTO-SOLVE ===
                
                if not auto_solved and not self._solving_active:
                    self.captcha_handler(message.channel, "Link")
                if self.bot.global_settings_dict["webhook"]["enabled"]:
                    await self.bot.webhookSender(
                        msg=f"-{self.bot.username} [+] CAPTCHA Detected",
                        desc=f"**User** : <@{self.bot.user.id}>\n**Link** : [OwO Captcha]({message.jump_url})",
                        colors="#00FFAF",
                        img_url="https://cdn.discordapp.com/emojis/1171297031772438618.png",
                        author_img_url="https://imgur.com/a/xwALH1U",
                        plain_text=(
                            f"<@{self.bot.global_settings_dict['webhook']['webhookUserIdToPingOnCaptcha']}>"
                            if self.bot.global_settings_dict['webhook']['webhookUserIdToPingOnCaptcha']
                            else None
                        ),
                        webhook_url=self.bot.global_settings_dict["webhook"].get("webhookCaptchaUrl", None),
                    )
                console_handler(self.bot.global_settings_dict["console"])

            elif "**☠ |** You have been banned" in message.content:
                self.bot.command_handler_status["captcha"] = True
                await self.bot.log(f"Ban detected!", "#d70000")
                
                # Add dashboard log for ban detected
                channel_name = get_channel_name(message.channel)
                self.bot.add_dashboard_log("captcha", f"Ban detected in {channel_name}! Bot stopped automatically", "error")
                
                self.captcha_handler(message.channel, "Ban")
                console_handler(self.bot.global_settings_dict["console"], captcha=False)
                if self.bot.global_settings_dict["webhook"]["enabled"]:
                    await self.bot.webhookSender(
                        msg=f"-{self.bot.username} [+] BAN Detected",
                        desc=f"**User** : <@{self.bot.user.id}>\n**Link** : [Ban Message]({message.jump_url})",
                        colors="#00FFAF",
                        img_url="https://cdn.discordapp.com/emojis/1213902052879503480.gif",
                        author_img_url="https://imgur.com/a/xwALH1U",
                        plain_text=(
                            f"<@{self.bot.global_settings_dict['webhook']['webhookUserIdToPingOnCaptcha']}>"
                            if self.bot.global_settings_dict["webhook"]["webhookUserIdToPingOnCaptcha"]
                            else None
                        ),
                        webhook_url=self.bot.global_settings_dict["webhook"].get("webhookCaptchaUrl", None),
                    )
            elif message.embeds:
                for embed in message.embeds:
                    items = {
                        embed.title if embed.title else "",
                        embed.author.name if embed.author else "",
                        embed.footer.text if embed.footer else "",
                    }
                    for i in items:
                        if any(b in clean(i) for b in list_captcha):
                            """clean function cleans the captcha message of unwanted symbols etc"""
                            self.bot.command_handler_status["captcha"] = True
                            await self.bot.log(f"Captcha detected...?", "#d70000")
                            
                            # Add dashboard log for embed captcha detected
                            channel_name = get_channel_name(message.channel)
                            self.bot.add_dashboard_log("captcha", f"Possible captcha detected in embed ({channel_name})! Bot stopped", "warning")
                            
                            break

                    if embed.fields:
                        for field in embed.fields:
                            if field.name and any(b in clean(field.name) for b in list_captcha):
                                self.bot.command_handler_status["captcha"] = True
                                await self.bot.log(f"Captcha detected...?", "#d70000")
                                
                                # Add dashboard log for field captcha detected
                                channel_name = get_channel_name(message.channel)
                                self.bot.add_dashboard_log("captcha", f"Possible captcha in embed field ({channel_name})! Bot stopped", "warning")
                                
                                break
                            if field.value and any(b in clean(field.value) for b in list_captcha):
                                self.bot.command_handler_status["captcha"] = True
                                await self.bot.log(f"Captcha detected...?", "#d70000")
                                
                                # Add dashboard log for field value captcha detected
                                channel_name = get_channel_name(message.channel)
                                self.bot.add_dashboard_log("captcha", f"Possible captcha in embed field value ({channel_name})! Bot stopped", "warning")
                                
                                break

async def setup(bot):
    await bot.add_cog(Captcha(bot))
