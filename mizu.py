# Standard Library
import asyncio
import itertools
import json
import logging
import os
import random
import signal
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import traceback
from importlib.metadata import version as import_ver
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import Thread

# Termux Detection (MUST be before discord import!)
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

# Third-Party Libraries
import aiosqlite
import aiohttp

# Discord import with Termux compatibility handling
try:
    import discord
    from discord.ext import commands, tasks
except ImportError as e:
    if "curl" in str(e).lower() and on_mobile:
        print("\033[1;33m" + "="*60)
        print("⚠️  TERMUX COMPATIBILITY MODE")
        print("="*60)
        print("[!] curl_cffi is not compatible with Termux")
        print("[!] Please install discord.py-self without curl_cffi:")
        print()
        print("    pip uninstall curl-cffi curl_cffi discord.py -y")
        print("    pip install discord.py-self aiohttp requests")
        print()
        print("See: Tutor/termux.md for full instructions")
        print("="*60 + "\033[m")
        sys.exit(1)
    else:
        print(f"\033[1;31m[x] Failed to import discord: {e}\033[m")
        sys.exit(1)

import pytz
import requests
from rich.align import Align
from rich.console import Console
from rich.panel import Panel

# Local
from utils.misspell import misspell_word
from utils import state
from dashboard import app

"""Cntrl+c detect"""
def handle_sigint(signal_number, frame):
    print("\nCtrl+C detected. stopping code!")
    os._exit(0)

signal.signal(signal.SIGINT, handle_sigint)

def compare_versions(current_version, latest_version):
    current_version = current_version.lstrip("v")
    latest_version = latest_version.lstrip("v")

    current = list(map(int, current_version.split(".")))
    latest = list(map(int, latest_version.split(".")))

    for c, l in zip(current, latest):
        if l > c:
            return True
        elif l < c:
            return False

    if len(latest) > len(current):
        return any(x > 0 for x in latest[len(current):])
    
    return False


def clear():
    os.system('cls') if os.name == 'nt' else os.system('clear')

console = Console()
lock = threading.Lock()
clear()


def load_accounts_dict(file_path="utils/stats.json"):
    with open(file_path, "r") as config_file:
        return json.load(config_file)

with open("config/global_settings.json", "r") as config_file:
    global_settings_dict = json.load(config_file)

with open("config/misc.json", "r") as config_file:
    misc_dict = json.load(config_file)


console.rule("[bold blue1]:>", style="navy_blue")
console_width = console.size.width
listUserIds = []


mizu_network_api = "https://api.ive.my.id"

mizuArt = r"""
 ███╗   ███╗██╗███████╗██╗   ██╗
 ████╗ ████║██║╚══███╔╝██║   ██║
 ██╔████╔██║██║  ███╔╝ ██║   ██║  
 ██║╚██╔╝██║██║ ███╔╝  ██║   ██║ 
 ██║ ╚═╝ ██║██║███████╗╚██████╔╝ 
 ╚═╝     ╚═╝╚═╝╚══════╝ ╚═════╝ 
M I Z U   N E T W O R K   水
"""
mizuPanel = Panel(Align.center(mizuArt), style="cyan ", highlight=False)
version = "1.3.0"
debug_print = True

def merge_dicts(main, small):
    for key, value in small.items():
        if key in main and isinstance(main[key], dict) and isinstance(value, dict):
            merge_dicts(main[key], value)
        else:
            main[key] = value

def get_from_db(command):
    with sqlite3.connect("utils/data/db.sqlite") as conn:
        conn.row_factory = sqlite3.Row 
        cur = conn.cursor()

        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        if mode.lower() != 'wal':
            cur.execute("PRAGMA journal_mode=WAL;")

        cur.execute(command)

        item = cur.fetchall()
        return item

# Global list to store real-time command logs (declared at top of file)
max_command_logs = 500  # Keep only the last 500 commands

def add_command_log(account_id, command_type, message, status="info"):
    """Add a command log entry"""
    # Use shared state
    log_entry = {
        "timestamp": time.time(),
        "account_id": str(account_id),
        "account_display": f"User-{str(account_id)[-4:]}",
        "command_type": command_type,
        "message": message,
        "status": status
    }
    
    state.command_logs.append(log_entry)
    
    # Keep only the last max_command_logs entries
    if len(state.command_logs) > state.max_command_logs:
        state.command_logs = state.command_logs[-state.max_command_logs:]

def refresh_bot_settings(changed_command=None, enabled=None):
    """Refresh settings for all active bot instances and apply immediate toggle if provided."""
    # Use shared state
    try:
        if not state.bot_instances:
            print("No active bot instances to refresh")
            return

        active_clients = []
        for client in state.bot_instances:
            try:
                if hasattr(client, 'refresh_settings') and hasattr(client, 'user') and client.user:
                    client.refresh_settings()
                    # Apply immediate toggle on the client's loop
                    if changed_command is not None and enabled is not None and hasattr(client, 'apply_toggle'):
                        asyncio.run_coroutine_threadsafe(client.apply_toggle(changed_command, enabled), client.loop)
                    active_clients.append(client)
                elif hasattr(client, 'refresh_commands_dict'):
                    client.refresh_commands_dict()
                    if changed_command is not None and enabled is not None and hasattr(client, 'apply_toggle'):
                        asyncio.run_coroutine_threadsafe(client.apply_toggle(changed_command, enabled), client.loop)
                    active_clients.append(client)
            except Exception as client_error:
                print(f"Error refreshing individual client: {client_error}")
                continue

        state.bot_instances = active_clients
        print(f"Refreshed settings for {len(active_clients)} active bot instances")

    except Exception as e:
        print(f"Error refreshing bot settings: {e}")
        enabled = data.get('enabled', False)
        
        if not command:
            return jsonify({"error": "Command not specified"}), 400
        
        # Update main settings file
        settings_path = "config/settings.json"
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            # Update the specific command setting
            if command == "hunt":
                settings["commands"]["hunt"]["enabled"] = enabled
            elif command == "battle":
                settings["commands"]["battle"]["enabled"] = enabled
            elif command == "daily":
                settings["autoDaily"] = enabled
            elif command == "owo":
                settings["commands"]["owo"]["enabled"] = enabled
            elif command == "useSlashCommands":
                settings["useSlashCommands"] = enabled
            elif command == "channelSwitcher":
                settings["channelSwitcher"]["enabled"] = enabled
            elif command == "stopHuntingWhenNoGems":
                settings["stopHuntingWhenNoGems"] = enabled
            
            # Save updated settings
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            # Log the change for all active bot instances
            for user_id in listUserIds:
                if command == "useSlashCommands":
                    add_command_log(user_id, "system", f"Slash commands {'enabled' if enabled else 'disabled'}", "info")
                elif command == "channelSwitcher":
                    add_command_log(user_id, "system", f"Channel Switcher {'enabled' if enabled else 'disabled'}", "info")
                elif command == "stopHuntingWhenNoGems":
                    add_command_log(user_id, "system", f"Stop Hunt When No Gems {'enabled' if enabled else 'disabled'}", "info")
                else:
                    add_command_log(user_id, "system", f"{command.upper()} {'enabled' if enabled else 'disabled'}", "info")
        
        # Refresh bot settings for all active instances and apply immediately
        refresh_bot_settings(command, enabled)
        
        # Create specific success messages
        command_names = {
            "hunt": "Hunt",
            "battle": "Battle", 
            "daily": "Daily",
            "owo": "OwO",
            "useSlashCommands": "Slash Commands",
            "channelSwitcher": "Channel Switcher",
            "stopHuntingWhenNoGems": "Stop Hunt When No Gems"
        }
        
        command_display = command_names.get(command, command.upper())
        status = "enabled" if enabled else "disabled"
        
        return jsonify({
            "success": True, 
            "message": f"✅ {command_display} {status} successfully!"
        })
        
    except Exception as e:
        print(f"Error toggling quick setting: {e}")
        return jsonify({"error": "Failed to toggle setting"}), 500

@app.route('/api/dashboard/quick-settings', methods=['GET'])
def get_quick_settings():
    """Get current quick settings status"""
    try:
        # Read from main settings file
        settings_path = "config/settings.json"
        
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            return jsonify({
                "hunt": settings.get("commands", {}).get("hunt", {}).get("enabled", False),
                "battle": settings.get("commands", {}).get("battle", {}).get("enabled", False), 
                "daily": settings.get("autoDaily", False),
                "owo": settings.get("commands", {}).get("owo", {}).get("enabled", False),
                "useSlashCommands": settings.get("useSlashCommands", False),
                "channelSwitcher": settings.get("channelSwitcher", {}).get("enabled", False),
                "stopHuntingWhenNoGems": settings.get("stopHuntingWhenNoGems", False)
            })
        else:
            return jsonify({"hunt": False, "battle": False, "daily": False, "owo": False, "useSlashCommands": False, "channelSwitcher": False, "stopHuntingWhenNoGems": False})
            
    except Exception as e:
        print(f"Error getting quick settings: {e}")
        return jsonify({"hunt": False, "battle": False, "daily": False, "owo": False, "useSlashCommands": False, "channelSwitcher": False, "stopHuntingWhenNoGems": False})

@app.route('/api/dashboard/security-settings', methods=['GET'])
def get_security_settings():
    """Get current security settings"""
    try:
        # Read from main settings file
        settings_path = "config/settings.json"
        
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            default_cooldowns = settings.get("defaultCooldowns", {})
            command_handler = default_cooldowns.get("commandHandler", {})
            between_commands = command_handler.get("betweenCommands", [1.7, 2.7])
            captcha_restart = default_cooldowns.get("captchaRestart", [3.7, 5.6])
            
            return jsonify({
                "delay_min": between_commands[0],
                "delay_max": between_commands[1],
                "captcha_restart_min": captcha_restart[0],
                "captcha_restart_max": captcha_restart[1],
                "typing_indicator": False,
                "random_delays": False,
                "silent_mode": settings.get("silentMode", False)
            })
        else:
            return jsonify({
                "delay_min": 1.7,
                "delay_max": 2.7,
                "captcha_restart_min": 3.7,
                "captcha_restart_max": 5.6,
                "typing_indicator": False,
                "random_delays": False,
                "silent_mode": False
            })
            
    except Exception as e:
        print(f"Error getting security settings: {e}")
        return jsonify({
            "delay_min": 1.7,
            "delay_max": 2.7,
            "captcha_restart_min": 3.7,
            "captcha_restart_max": 5.6,
            "typing_indicator": False,
            "random_delays": False,
            "silent_mode": False
        })

@app.route('/api/dashboard/security-settings', methods=['POST'])
def save_security_settings():
    """Save security settings"""
    try:
        data = request.get_json()
        
        # Update main settings file
        settings_path = "config/settings.json"
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            # Update delay settings
            if "defaultCooldowns" not in settings:
                settings["defaultCooldowns"] = {}
            if "commandHandler" not in settings["defaultCooldowns"]:
                settings["defaultCooldowns"]["commandHandler"] = {}
            
            settings["defaultCooldowns"]["commandHandler"]["betweenCommands"] = [
                float(data.get("delay_min", 1.7)),
                float(data.get("delay_max", 2.7))
            ]
            
            settings["defaultCooldowns"]["captchaRestart"] = [
                float(data.get("captcha_restart_min", 3.7)),
                float(data.get("captcha_restart_max", 5.6))
            ]
            
            # Anti-Detection removed from UI; enforce safe defaults
            settings["typingIndicator"] = False
            settings["randomDelays"] = False
            settings["silentMode"] = data.get("silent_mode", False)
            
            # Save updated settings
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            # Log the change for all active bot instances
            for user_id in listUserIds:
                add_command_log(user_id, "system", "Security settings updated", "info")
        
        # Refresh bot settings for all active instances
        refresh_bot_settings()
        
        return jsonify({
            "success": True,
            "message": "Security settings saved successfully"
        })
        
    except Exception as e:
        print(f"Error saving security settings: {e}")
        return jsonify({"error": "Failed to save security settings"}), 500

@app.route('/api/dashboard/gambling-settings', methods=['GET'])
def get_gambling_settings():
    """Get current Gambling settings"""
    try:
        settings_path = "config/settings.json"
        
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            gamble = settings.get("gamble", {})
            
            return jsonify({
                "allottedAmount": gamble.get("allottedAmount", 30000),
                "goalSystem": gamble.get("goalSystem", {
                    "enabled": False,
                    "amount": 300
                }),
                "coinflip": gamble.get("coinflip", {
                    "enabled": False,
                    "startValue": 200,
                    "multiplierOnLose": 2,
                    "cooldown": [16, 18],
                    "options": ["t"]
                }),
                "slots": gamble.get("slots", {
                    "enabled": False,
                    "startValue": 200,
                    "multiplierOnLose": 2,
                    "cooldown": [16, 18]
                })
            })
        else:
            # Return default values
            return jsonify({
                "allottedAmount": 30000,
                "goalSystem": {
                    "enabled": False,
                    "amount": 300
                },
                "coinflip": {
                    "enabled": False,
                    "startValue": 200,
                    "multiplierOnLose": 2,
                    "cooldown": [16, 18],
                    "options": ["t"]
                },
                "slots": {
                    "enabled": False,
                    "startValue": 200,
                    "multiplierOnLose": 2,
                    "cooldown": [16, 18]
                }
            })
            
    except Exception as e:
        print(f"Error getting Gambling settings: {e}")
        return jsonify({"error": "Failed to get Gambling settings"}), 500

@app.route('/api/dashboard/gambling-settings', methods=['POST'])
def save_gambling_settings():
    """Save Gambling settings"""
    try:
        data = request.get_json()
        
        settings_path = "config/settings.json"
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            # Update Gambling settings
            if "gamble" not in settings:
                settings["gamble"] = {}
            
            settings["gamble"]["allottedAmount"] = int(data.get("allottedAmount", 30000))
            settings["gamble"]["goalSystem"] = data.get("goalSystem", {
                "enabled": False,
                "amount": 300
            })
            
            # Coinflip settings
            coinflip = data.get("coinflip", {})
            settings["gamble"]["coinflip"] = {
                "enabled": coinflip.get("enabled", False),
                "startValue": int(coinflip.get("startValue", 200)),
                "multiplierOnLose": float(coinflip.get("multiplierOnLose", 2)),
                "cooldown": coinflip.get("cooldown", [16, 18]),
                "options": coinflip.get("options", ["t"])
            }
            
            # Slots settings
            slots = data.get("slots", {})
            settings["gamble"]["slots"] = {
                "enabled": slots.get("enabled", False),
                "startValue": int(slots.get("startValue", 200)),
                "multiplierOnLose": float(slots.get("multiplierOnLose", 2)),
                "cooldown": slots.get("cooldown", [16, 18])
            }
            
            # Save updated settings
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            # Log the change for all active bot instances
            for user_id in listUserIds:
                add_command_log(user_id, "system", "Gambling settings updated", "info")
        
        # Refresh bot settings for all active instances
        refresh_bot_settings()
        
        return jsonify({
            "success": True,
            "message": "Gambling settings saved successfully"
        })
        
    except Exception as e:
        print(f"Error saving Gambling settings: {e}")
        return jsonify({"error": "Failed to save Gambling settings"}), 500



@app.route('/api/dashboard/quest-tracker', methods=['GET'])
def get_quest_tracker():
    """Get quest tracker status and progress"""
    try:
        quest_data = {
            "enabled": False,
            "quests": {},
            "rare_catches": {"mythical": 0, "fabled": 0, "legendary": 0},
            "detected": False
        }
        
        # Get quest data from active bot instances
        for client in bot_instances:
            if hasattr(client, 'user') and client.user:
                # Try to get quest cog
                quest_cog = client.get_cog('Quest')
                if quest_cog:
                    quest_status = quest_cog.get_quest_status()
                    quest_data = {
                        "enabled": True,
                        "quests": quest_status["quests"],
                        "rare_catches": quest_status["rare_catches"],
                        "detected": quest_status["detected"]
                    }
                    break
                    
        return jsonify(quest_data)
        
    except Exception as e:
        print(f"Error getting quest tracker: {e}")
        return jsonify({
            "enabled": False,
            "quests": {},
            "rare_catches": {"mythical": 0, "fabled": 0, "legendary": 0},
            "detected": False
        })

@app.route('/api/dashboard/quest-tracker-settings', methods=['GET'])
def get_quest_tracker_settings():
    """Get quest tracker settings"""
    try:
        settings_path = "config/settings.json"
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            quest_settings = settings.get("questTracker", {})
            return jsonify({
                "enabled": quest_settings.get("enabled", False),
                "autoCheckQuests": quest_settings.get("autoCheckQuests", True),
                "notifications": quest_settings.get("notifications", True),
                "logRareAnimals": quest_settings.get("logRareAnimals", True),
                "trackProgress": quest_settings.get("trackProgress", True),
                "notifyOnCompletion": quest_settings.get("notifyOnCompletion", True)
            })
        else:
            return jsonify({
                "enabled": False,
                "autoCheckQuests": True,
                "notifications": True,
                "logRareAnimals": True,
                "trackProgress": True,
                "notifyOnCompletion": True
            })
            
    except Exception as e:
        print(f"Error getting quest tracker settings: {e}")
        return jsonify({"error": "Failed to get quest tracker settings"}), 500

@app.route('/api/dashboard/quest-tracker-settings', methods=['POST'])
def save_quest_tracker_settings():
    """Save quest tracker settings"""
    try:
        data = request.get_json()
        
        settings_path = "config/settings.json"
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            settings["questTracker"] = {
                "enabled": data.get("enabled", False),
                "autoCheckQuests": data.get("autoCheckQuests", True),
                "notifications": data.get("notifications", True),
                "logRareAnimals": data.get("logRareAnimals", True),
                "trackProgress": data.get("trackProgress", True),
                "notifyOnCompletion": data.get("notifyOnCompletion", True)
            }
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            # Log the change
            for user_id in listUserIds:
                add_command_log(user_id, "system", "Quest Tracker settings updated", "info")
        
        # Refresh bot settings
        refresh_bot_settings()
        
        return jsonify({
            "success": True,
            "message": "Quest Tracker settings saved successfully"
        })
        
    except Exception as e:
        print(f"Error saving quest tracker settings: {e}")
        return jsonify({"error": "Failed to save quest tracker settings"}), 500

@app.route('/api/dashboard/command-logs', methods=['GET'])
def get_command_logs():
    """Get real-time command logs for dashboard"""
    try:
        # Get query parameters for filtering
        log_type = request.args.get('type', 'all')
        account_id = request.args.get('account', 'all')
        limit = int(request.args.get('limit', 100))
        
        # Filter logs
        filtered_logs = command_logs
        
        if log_type != 'all':
            filtered_logs = [log for log in filtered_logs if log['command_type'] == log_type]
        
        if account_id != 'all':
            filtered_logs = [log for log in filtered_logs if log['account_id'] == account_id]
        
        # Get the most recent logs
        recent_logs = filtered_logs[-limit:] if len(filtered_logs) > limit else filtered_logs
        
        # Format timestamps for display
        for log in recent_logs:
            log['formatted_time'] = time.strftime("%H:%M:%S", time.localtime(log['timestamp']))
        
        return jsonify({
            "logs": recent_logs,
            "total_count": len(command_logs),
            "filtered_count": len(filtered_logs)
        })
    except Exception as e:
        print(f"Error fetching command logs: {e}")
        return jsonify({"logs": [], "total_count": 0, "filtered_count": 0})

@app.route('/api/dashboard/terminate', methods=['POST'])
def dashboard_terminate():
    """Terminate all bot instances and exit process (on purpose)."""
    try:
        # Close all discord clients gracefully
        for client in list(bot_instances):
            try:
                if hasattr(client, 'close'):
                    asyncio.run_coroutine_threadsafe(client.close(), client.loop)
            except Exception:
                pass
        # Also try to stop the web server by signaling exit
        def delayed_exit():
            time.sleep(0.5)
            os._exit(0)
        Thread(target=delayed_exit, daemon=True).start()
        return jsonify({"success": True, "message": "Termination signal sent. Shutting down..."})
    except Exception as e:
        print(f"Error terminating bot: {e}")
    cli = sys.modules["flask.cli"]
    cli.show_server_banner = lambda *x: None
    app.run(
        debug=False,
        use_reloader=False,
        port=global_settings_dict["website"]["port"],
        host="0.0.0.0" if global_settings_dict["website"]["enableHost"] else "127.0.0.1",
    )


def web_start():
    flaskLog = logging.getLogger("werkzeug")
    flaskLog.disabled = True
    cli = sys.modules["flask.cli"]
    cli.show_server_banner = lambda *x: None
    app.run(
        debug=False,
        use_reloader=False,
        port=global_settings_dict["website"]["port"],
        host="0.0.0.0" if global_settings_dict["website"]["enableHost"] else "127.0.0.1",
    )


""""""

def printBox(text, color, title=None):
    test_panel = Panel(text, style=color, title=title)
    if not misc_dict["console"]["compactMode"]:
        console.print(test_panel)
    else:
        console.print(text, style=color)

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package_name])

# Note: is_termux() and on_mobile already defined at the top of the file (line 22-33)

if not on_mobile and not misc_dict["hostMode"]:
    try:
        if global_settings_dict["batteryCheck"]["enabled"]:
            import psutil
    except Exception as e:
        print(f"ImportError: {e}")


# For time related stuff
def get_weekday():
    # 0 = monday, 6 = sunday
    return str(datetime.today().weekday())

def get_hour():
    # only from 0 to 23 (24hr format)
    return datetime.now().hour

def get_date():
    return datetime.now().date().isoformat()  # e.g. "2025-05-31"


# For battery check
def batteryCheckFunc():
    cnf = global_settings_dict["batteryCheck"]
    try:
        if on_mobile:
            while True:
                time.sleep(cnf["refreshInterval"])
                try:
                    battery_status = os.popen("termux-battery-status").read()
                except Exception as e:
                    console.print(
                        f"system - Battery check failed!!".center(console_width - 2),
                        style="red ",
                    )
                battery_data = json.loads(battery_status)
                percentage = battery_data["percentage"]
                console.print(
                    f"system - Current battery •> {percentage}".center(console_width - 2),
                    style="blue ",
                )
                if percentage < int(cnf["minPercentage"]):
                    break
        else:
            while True:
                time.sleep(cnf["refreshInterval"])
                try:
                    battery = psutil.sensors_battery()
                    if battery is not None:
                        percentage = int(battery.percent)
                        console.print(
                            f"system - Current battery •> {percentage}".center(console_width - 2),
                            style="blue ",
                        )
                        if percentage < int(cnf["minPercentage"]):
                            break
                except Exception as e:
                    console.print(
                        f"-system - Battery check failed!!.".center(console_width - 2),
                        style="red ",
                    )
    except Exception as e:
        print("battery check", e)
    os._exit(0)

if global_settings_dict["batteryCheck"]["enabled"]:
    loop_thread = threading.Thread(target=batteryCheckFunc, daemon=True)
    loop_thread.start()

def popup_main_loop():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    while True:
        msg, username, channelname, captchatype = popup_queue.get()
        print(msg, username, channelname, captchatype)
        # Create a new popup window
        popup = tk.Toplevel(root)
        popup.configure(bg="#000000")
        try:
            icon_path = "static/imgs/logo.png"  # Path to your icon image file
            icon = tk.PhotoImage(file=icon_path)
            popup.iconphoto(True, icon)
        except Exception as e:
            print(f"Failed to load icon: {e}")
        # Determine screen dimensions
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        # Calculate popup window position and size
        popup_width = min(500, int(screen_width * 0.8))  # Limit maximum width to 500px or 80% of screen width
        popup_height = min(300, int(screen_height * 0.8))  # Limit maximum height to 300px or 80% of screen height
        x_position = (screen_width - popup_width) // 2
        y_position = (screen_height - popup_height) // 2
        popup.geometry(f"{popup_width}x{popup_height}+{x_position}+{y_position}")
        popup.title("Mizu Network - Notifs")
        label_text = msg.format(username=username, channelname=channelname, captchatype=captchatype)
        label = tk.Label(
            popup, 
            text=label_text, 
            wraplength=popup_width - 40, 
            justify="left", 
            padx=20, 
            pady=20, 
            bg="#000000", 
            fg="#be7dff"
        )
        label.pack(fill="both", expand=True)
        button = tk.Button(popup, text="OK", command=popup.destroy)
        button.pack(pady=10)
        try:
            popup.grab_set()  # Restrict input focus to the popup
        except tk.TclError as e:
            print(f"Grab failed: {e}")
        finally:
            popup.focus_set()  # Ensure the popup has focus
            popup.lift()  # Bring the popup to the top

        popup.wait_window()


class MyClient(commands.Bot):

    def __init__(self, token, channel_id, global_settings_dict, *args, **kwargs):
        # Handle intents for compatibility with different discord.py-self versions
        # Some versions (especially in Termux) require intents parameter
        if 'intents' not in kwargs:
            try:
                # Try to create intents if the attribute exists
                if hasattr(discord, 'Intents'):
                    intents = discord.Intents.default()
                    intents.messages = True
                    intents.guilds = True
                    intents.message_content = True
                    kwargs['intents'] = intents
            except (AttributeError, Exception):
                # If intents don't exist or fail, continue without them
                # This is normal for older versions of discord.py-self
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

        # discord.py-self's module sets global random to fixed seed. reset that, locally.
        self.random = random.Random()

        # Task: Update code to have checks using status instead of individual variables
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
        global config_updated
        if config_updated is not None and (time.time() - config_updated < 6):
            await self.update_config()
            # config_updated = False

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
            safety_check = requests.get(f"{mizu_network_api}/safety_check.json", timeout=10).json()
            latest_version = requests.get(f"{mizu_network_api}/version.json", timeout=10).json()

            if safety_check.get("enabled", False) and compare_versions(version, safety_check.get("version", "0.0.0")):
                self.command_handler_status["captcha"] = True
                await self.log(f"🛑 Safety Check Alert!\nReason: {safety_check.get('reason', 'Unknown')}\n(Triggered by {safety_check.get('author', 'System')})", "#5c0018")
                
                # Add dashboard log for safety check
                self.add_dashboard_log("system", f"Safety check triggered! Bot stopped: {safety_check.get('reason', 'Unknown')}", "error")
                
                if compare_versions(latest_version.get("version", "0.0.0"), safety_check.get("version", "0.0.0")):
                    await self.log(f"Please update to: v{latest_version.get('version', 'latest')}", "#33245e")
        except requests.exceptions.RequestException:
            # Network error, silently pass to avoid spam
            pass
        except Exception as e:
            await self.log(f"Failed to perform safety check: {str(e)}", "#c25560")

    async def start_cogs(self):
        files = os.listdir(resource_path("./cogs"))  # Get the list of files
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
        async with aiosqlite.connect("utils/data/db.sqlite", timeout=5) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute("BEGIN;")
            await db.execute(sql, params)
            await db.commit()

    async def get_from_db(self, sql, params=None):
        async with aiosqlite.connect("utils/data/db.sqlite", timeout=5) as db:
            # allows dictionary-like access
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, params or ()) as cursor:
                result = await cursor.fetchall()
                return result

    async def update_cash_db(self):
        """Update values in database"""
        hr = get_hour()

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
        today_str = get_date()

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
            # Handle gap between cowoncy chart
            cur_hr = get_hour()
            last_cash = 0
            for hr in range(cur_hr+1):
                hr_row = await self.get_from_db(
                    "SELECT earnings FROM cowoncy_earnings WHERE user_id = ? AND hour = ?", 
                    (self.user.id, hr)
                )
                # Note: negative values are allowed.
                if hr_row and hr_row[0]["earnings"] != 0:
                    last_cash = hr_row[0]["earnings"]
                elif last_cash != 0:
                    await self.update_database(
                        "UPDATE cowoncy_earnings SET earnings = ? WHERE hour = ? AND user_id = ?",
                        (last_cash, hr, self.user.id)
                    )
            # Return once done as we don't want reset.
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
        today_str = get_date()

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
        hr = get_hour()

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
        # Check if huntbot is active - only disable conflicting commands
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
            "gems": self.settings_dict["autoUse"]["gems"]["enabled"],  # Gems can work with huntbot
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
        """Add a command log entry to the dashboard"""
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
            
            # Keep only the last max_command_logs entries
            if len(state.command_logs) > state.max_command_logs:
                state.command_logs = state.command_logs[-state.max_command_logs:]
        except Exception as e:
            print(f"Error adding dashboard log: {e}")
    
    
    def refresh_settings(self):
        """Refresh bot settings from file"""
        try:
            settings_path = f"config/{self.user.id}/settings.json"
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    new_settings = json.load(f)
                self.settings_dict = new_settings
                self.refresh_commands_dict()
                # Ensure loaded cogs reflect new settings
                asyncio.create_task(self.sync_cogs_with_settings())
                print(f"Settings refreshed for user {self.user.id}")
        except Exception as e:
            print(f"Error refreshing settings for user {self.user.id}: {e}")

    async def purge_from_queue(self, command_id):
        """Remove all queued items for a given command id immediately."""
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
        """Load/unload cogs to match current settings_dict/commands_dict."""
        try:
            self.refresh_commands_dict()
            files = os.listdir(resource_path("./cogs"))
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
        """Apply a single command toggle immediately (load/unload + purge queue)."""
        try:
            # Ensure settings_dict is the latest
            await asyncio.sleep(0)  # yield control
            self.refresh_commands_dict()
            
            # Handle useSlashCommands setting
            if command == "useSlashCommands":
                self.settings_dict["useSlashCommands"] = enabled
                await self.log(f"Slash commands {'enabled' if enabled else 'disabled'}", "#40e0d0")
                # Add dashboard log
                self.add_dashboard_log("system", f"Slash commands {'enabled' if enabled else 'disabled'}", "info")
                return
            
            # Handle channelSwitcher setting
            if command == "channelSwitcher":
                # Ensure channelSwitcher exists in settings_dict
                if "channelSwitcher" not in self.settings_dict or self.settings_dict["channelSwitcher"] is None:
                    self.settings_dict["channelSwitcher"] = {
                        "enabled": False, 
                        "users": [], 
                        "interval": [300, 600], 
                        "delayBeforeSwitch": [2, 4]
                    }
                
                self.settings_dict["channelSwitcher"]["enabled"] = enabled
                await self.log(f"Channel Switcher {'enabled' if enabled else 'disabled'}", "#9dc3f5")
                # Add dashboard log
                self.add_dashboard_log("system", f"Channel Switcher {'enabled' if enabled else 'disabled'}", "info")
                
                # Load or unload the channelswitcher cog
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
                    # Add dashboard log
                    self.add_dashboard_log("system", f"{command.upper()} disabled", "warning")
                elif enabled and extension not in self.extensions and self.commands_dict.get(command, False):
                    try:
                        await self.load_extension(extension)
                        await self.log(f"{command.upper()} enabled", "#51cf66")
                        # Add dashboard log
                        self.add_dashboard_log("system", f"{command.upper()} enabled", "success")
                    except Exception as e:
                        await self.log(f"Error - Failed to load extension {extension}: {e}", "#c25560")
                        # Add dashboard log
                        self.add_dashboard_log("system", f"Failed to enable {command.upper()}: {e}", "error")

            # Purge queued items and checks for this command
            await self.remove_queue(id=command)
            await self.purge_from_queue(command)
        except Exception as e:
            await self.log(f"Error - apply_toggle({command}): {e}", "#c25560")
            # Add dashboard log
            self.add_dashboard_log("system", f"Error toggling {command.upper()}: {e}", "error")

    """To make the code cleaner when accessing cooldowns from config."""
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
            # Check if cmd_data has required 'id' field
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
                # Ensure command already in queue is not readded to prevent spam
                await self.log(f"Error - command with id: {cmd_data['id']} already in queue, being attempted to be added back.", "#c25560")
                return

            # Get priority
            priority_int = cnf[cmd_data["id"]].get("priority") if not quick else 0
            if not priority_int and priority_int!=0:
                await self.log(f"Error - command with id: {cmd_data['id']} do not have a priority set in misc.json", "#c25560")
                return

            async with self.lock:
                await self.queue.put((
                    priority_int,  # Priority to sort commands with
                    next(self.cmd_counter),               # A counter to serve as a tie-breaker
                    deepcopy(cmd_data)                # actual data
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
        with lock:
            popup_queue.put(
                (
                    (
                        global_settings_dict["captcha"]["toastOrPopup"]["captchaContent"]
                        if captcha_type != "Ban"
                        else global_settings_dict["captcha"]["toastOrPopup"]["bannedContent"]
                    ),
                    self.user.name,
                    channel_name,
                    captcha_type,
                )
            )

    async def log(self, text, color="#ffffff", bold=False, web_log=global_settings_dict["website"]["enabled"], webhook_useless_log=global_settings_dict["webhook"]["webhookUselessLog"]):
        # Use shared state
        current_time = datetime.now().strftime("%H:%M:%S")
        if self.misc["debug"]["enabled"]:
            frame_info = traceback.extract_stack()[-2]
            filename = os.path.basename(frame_info.filename)
            lineno = frame_info.lineno

            content_to_print = f"[#676585]❲{current_time}❳[/#676585] {self.username} - {text} | [#676585]❲{filename}:{lineno}❳[/#676585]"
            console.print(
                content_to_print,
                style=color,
                markup=True
            )
            with lock:
                if self.misc["debug"]["logInTextFile"]:
                    with open("logs.txt", "a") as log:
                        log.write(f"{content_to_print}\n")
        else:
            console.print(f"{self.username}| {text}".center(console_width - 2), style=color)
        if web_log:
            with lock:
                state.website_logs.append(f"<div class='message'><span class='timestamp'>[{current_time}]</span><span class='text'>{self.username}| {text}</span></div>")
                if len(state.website_logs) > 300:
                    state.website_logs.pop(0)
        if webhook_useless_log:
            await self.webhookSender(footer=f"[{current_time}] {self.username} - {text}", colors=color)

    async def webhookSender(self, msg=None, desc=None, plain_text=None, colors=None, img_url=None, author_img_url=None, footer=None, webhook_url=None):
        try:
            if colors:
                if isinstance(colors, str) and colors.startswith("#"):
                    """Convert to hexadecimal value"""
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
        command = command.replace(" ", "")  # Remove spaces for accurate timing
        base_delay = self.random_float(self.settings_dict["misspell"]["baseDelay"]) 
        rectification_time = sum(self.random_float(self.settings_dict["misspell"]["errorRectificationTimePerLetter"]) for _ in command)  
        total_time = base_delay + rectification_time
        return total_time

    # send commands
    async def send(self, message, color=None, bypass=False, channel=None, silent=global_settings_dict["silentTextMessages"], typingIndicator=global_settings_dict["typingIndicator"]):
        """
            TASK: Refactor
        """

        if not channel:
            channel = self.cm
        disable_log = self.misc["console"]["disableCommandSendLog"]
        msg = message
        misspelled = False
        if self.settings_dict["misspell"]["enabled"]:
            if self.random.uniform(1,100) < self.settings_dict["misspell"]["frequencyPercentage"]:
                msg = misspell_word(message)
                misspelled = True
                # left off here!

        """
        TASK: remove repition here
        """
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
                time = self.calculate_correction_time(message)
                await self.log(f"correcting: {msg} -> {message} in {time}s", "#422052")
                await asyncio.sleep(time)
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
        pst_timezone = pytz.timezone('US/Pacific') #gets timezone
        current_time_pst = datetime.now(timezone.utc).astimezone(pst_timezone) #current pst time
        midnight_pst = pst_timezone.localize(datetime(current_time_pst.year, current_time_pst.month, current_time_pst.day, 0, 0, 0)) #gets 00:00 of the day
        time_until_12am_pst = midnight_pst + timedelta(days=1) - current_time_pst # adds a day to the midnight to get time till next midnight, then subract it with current time
        total_seconds = time_until_12am_pst.total_seconds() # turn that time to seconds
        # 12am = 00:00, I might need this the next time I take a look here.
        return total_seconds

    def time_in_seconds(self):
        """
        timestamp is basically seconds passed after 1970 jan 1st
        """
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
        
        # Check for auto-sell trigger after cash update
        if self.settings_dict.get("autoSell", {}).get("enabled", False):
            try:
                autosell_cog = self.get_cog("AutoSell")
                if autosell_cog:
                    await autosell_cog.check_balance_and_auto_sell()
            except Exception as e:
                await self.log(f"Error checking auto-sell: {e}", "#c25560")

    async def setup_hook(self):
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

        printBox(f'-Loaded {self.username}[*].'.center(console_width - 2), 'bold royal_blue1 ')
        listUserIds.append(self.user.id)
        

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

        # self.dm = await (await self.fetch_user(self.owo_bot_id)).create_dm()
        # remove temp fix in `cogs/captcha.py` if uncommenting

        # Fetch slash commands in self.cm
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

        with lock:
            accounts_dict = load_accounts_dict()
            if str(self.user.id) not in accounts_dict:
                accounts_dict.update(self.default_config)
                with open("utils/stats.json", "w") as f:
                    json.dump(accounts_dict, f, indent=4)

        # Charts
        await self.populate_stats_db()

        await self.populate_cowoncy_earnings()
        await self.reset_gamble_wins_or_losses()

        await self.fetch_net_earnings()

        # Start various tasks and updates
        # self.config_update_checker.start()
        # disabled since unnecessory

        await asyncio.sleep(self.random_float(global_settings_dict["account"]["startupDelay"]))
        await self.update_config()

        if self.global_settings_dict["offlineStatus"]:
            self.presence.start()

        if self.settings_dict["sleep"]["enabled"]:
            self.random_sleep.start()

        if self.settings_dict["cashCheck"]:
            asyncio.create_task(self.check_for_cash())

def get_local_ip():
    if not global_settings_dict["website"]["enableHost"]:
        return 'localhost'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            """10.255.255.255 is fake"""
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
    except Exception:
        return 'localhost'


"""Handle Weekly runtime"""
def handle_weekly_runtime(path="utils/data/weekly_runtime.json"):
    while True:
        try:
            with open(path, "r") as config_file:
                weekly_runtime_dict = json.load(config_file)
            weekday = get_weekday()

            if weekly_runtime_dict[weekday][0] == 0:
                weekly_runtime_dict[weekday][0], weekly_runtime_dict[weekday][1] = time.time(), time.time()
            else:
                weekly_runtime_dict[weekday][1] = time.time()

            with open(path, "w") as f:
                json.dump(weekly_runtime_dict, f, indent=4)

        except Exception as e:
            print(f"Error when handling weekly runtime:\n{e}")

        # update every 15 seconds
        time.sleep(15)

def start_runtime_loop(path="utils/data/weekly_runtime.json"):
    try:
        with open(path, "r") as config_file:
            weekly_runtime_dict = json.load(config_file)

        now = time.time()
        last_checked = weekly_runtime_dict.get("last_checked", 0)

        if now - last_checked > 604800: # 604800 -> seconds in a week
            for day in map(str, range(7)):
                weekly_runtime_dict[day] = [0, 0]

        weekly_runtime_dict["last_checked"] = now

        with open(path, "w") as f:
            json.dump(weekly_runtime_dict, f, indent=4)

        loop_thread = threading.Thread(target=handle_weekly_runtime, daemon=True)
        loop_thread.start()

    except Exception as e:
        print(f"Error when attempting to start runtime handler:\n{e}")


"""Create SQLight database"""
def create_database(db_path="utils/data/db.sqlite"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute(
        "CREATE TABLE IF NOT EXISTS commands (name TEXT PRIMARY KEY, count INTEGER)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS cowoncy_earnings (user_id TEXT, hour INTEGER, earnings INTEGER, PRIMARY KEY (user_id, hour))"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS gamble_winrate (hour INTEGER PRIMARY KEY, wins INTEGER, losses INTEGER, net INTEGER)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS user_stats (user_id TEXT PRIMARY KEY, daily REAL, lottery REAL, cookie REAL, giveaways REAL, captchas INTEGER, cowoncy INTEGER)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS meta_data (key TEXT PRIMARY KEY, value INTEGER)"
    )
    # Switch to WAL mode.
    c.execute("PRAGMA journal_mode=WAL;")

    # Populate

    # -- gamble_winrate
    for hr in range(24):
        # hour does not have 24 in 24 hr format!!
        c.execute("INSERT OR IGNORE INTO gamble_winrate (hour, wins, losses, net) VALUES (?, ?, ?, ?)", (hr, 0, 0, 0))

    # -- meta data
    c.execute("INSERT OR IGNORE INTO meta_data (key, value) VALUES (?, ?)", ("gamble_winrate_last_checked", 0))
    c.execute("INSERT OR IGNORE INTO meta_data (key, value) VALUES (?, ?)", ("cowoncy_earnings_last_checked", 0))

    # -- commands
    for cmd in misc_dict["command_info"].keys():
        c.execute("INSERT OR IGNORE INTO commands (name, count) VALUES (?, ?)", (cmd, 0))

    # -- end --#
    conn.commit()
    conn.close()


# ----------STARTING BOT----------#
def fetch_json(url, description="data"):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        printBox(f"Failed to fetch {description}: {e}", "bold red")
        return {}

def fetch_mizu_api(endpoint):
    """Fetch data from Mizu OwO API endpoints"""
    try:
        url = f"{mizu_network_api}/{endpoint}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        printBox(f"Failed to fetch from Mizu API ({endpoint}): {e}", "bold red")
        return {}

def check_api_status():
    """Check if Mizu OwO API is accessible"""
    try:
        response = requests.get(mizu_network_api, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_api_announcements():
    """Get current announcements from API"""
    return fetch_mizu_api("announcements.json")

def get_api_features():
    """Get available features from API"""
    return fetch_mizu_api("features.json")

def get_api_themes():
    """Get available themes from API"""
    return fetch_mizu_api("themes.json")

def get_api_status():
    """Get system status from API"""
    return fetch_mizu_api("status.json")



def run_bots(tokens_and_channels):
    threads = []
    for token, channel_id in tokens_and_channels:
        thread = Thread(target=run_bot, args=(token, channel_id, global_settings_dict))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()




def run_bot(token, channel_id, global_settings_dict):
    """Original run_bot function for backwards compatibility"""
    # Use shared state
    
    # Create and set event loop for this thread (required for Termux compatibility)
    # In some environments (especially Termux), threads don't have an event loop by default
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        logging.getLogger("discord.client").setLevel(logging.ERROR)

        while True:
            client = MyClient(token, channel_id, global_settings_dict)
            
            # Add client to global instances list
            state.bot_instances.append(client)

            if not on_mobile:
                try:
                    client.run(token, log_level=logging.ERROR)

                except CurlError as e:
                    if "WS_SEND" in str(e) and "55" in str(e):
                        printBox("Broken pipe error detected. Restarting bot...", "bold red")
                        # Restart the loop with a new client instance.
                        continue 
                    else:
                        printBox(f"Curl error: {e}", "bold red")
                        # Don't retry unknown curl errors.
                        break 
                except Exception as e:
                    printBox(f"Unknown error when running bot: {e}", "bold red")

            else:
                # Mobile (Termux) uses an older version without curl_cffi.
                # No need to handle error in such cases.
                try:
                    client.run(token, log_level=logging.ERROR)
                except Exception as e:
                    printBox(f"Unknown error when running bot: {e}", "bold red")
                break 

    except Exception as e:
        printBox(f"Error starting bot: {e}", "bold red")

def install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package_name])

if __name__ == "__main__":
    # Version check disabled to prevent reinstall loop
    # try:
    #     discord_cur_version = import_ver("discord.py-self")
    #     discord_req_version = "2.1.0a5097+g20ae80b3"
    #     if discord_cur_version != discord_req_version:
    #         install_package("git+https://github.com/dolfies/discord.py-self@20ae80b398ec83fa272f0a96812140e14868c88f")
    #         raise SystemExit("discord.py-self was reinstalled. Please restart the program.")
    # except ImportError as e:
    #     print(e)
    pass

    if not misc_dict["console"]["compactMode"]:
        console.print(mizuPanel)
        console.rule(f"[bold blue1]version - {version}", style="navy_blue")
    

    # if check_api_status():
    #     printBox("🌊 Mizu OwO API - Connected", "bold cyan")
    # else:
    #     printBox("⚠️ Mizu OwO API - Connection Failed", "bold yellow")
    # 
    # version_json = fetch_mizu_api("version.json")
    #
    # # Only check version if API fetch was successful
    # if version_json and "version" in version_json:
    #     if compare_versions(version, version_json["version"]):
    #         printBox(f"""Update Detected - {version_json["version"]}
    # Changelog:-
    #     {version_json["changelog"]}""",'bold gold3')
    #         if version_json.get("important_update", False):
    #             printBox('It is reccomended to update....','bold light_yellow3' )
    # else:
    #     printBox("⚠️ Could not check for updates - API unavailable", "bold yellow")

    tokens_and_channels = [line.strip().split() for line in open("tokens.txt", "r")]
    token_len = len(tokens_and_channels)

    printBox(f'-Recieved {token_len} tokens.'.center(console_width - 2 ),'bold cyan' )

    # Create database or modify if required
    create_database()

    # Weekly runtime thread
    start_runtime_loop()

    if global_settings_dict["website"]["enabled"]:
        # Start website
        web_thread = threading.Thread(target=web_start)
        web_thread.start()
        # get ip
        ip = get_local_ip()
        printBox(f'Website Dashboard: http://{ip}:{global_settings_dict["website"]["port"]}'.center(console_width - 2 ), 'bold cyan')
    try:
        if misc_dict["news"]:
            # Fetch news from API
            news_json = fetch_mizu_api("news.json")
            if news_json.get("available"):
                printBox(
                    f'{news_json.get("content", "no content found..? this is an error! should be safe to ignore")}'.center(console_width - 2),
                    f"bold {news_json.get('color', 'white')}",
                    title=news_json.get("title", "📢 News")
                )
            
            # Fetch and display announcements from API
            announcements_json = get_api_announcements()
            if announcements_json.get("current_announcements"):
                for announcement in announcements_json["current_announcements"]:
                    if announcement.get("show_on_startup", True):
                        printBox(
                            f'{announcement.get("message", "")}'.center(console_width - 2),
                            f"bold {announcement.get('color', '#4fd1c7')}",
                            title=announcement.get("title", "📢 Announcement")
                        )
    except Exception as e:
        print(f"Error - {e}, while attempting to fetch news and announcements")

    if not misc_dict["console"]["hideStarRepoMessage"]:
        console.print("Star the repo in our github page if you want us to continue maintaining this proj :>.", style = "thistle1")
    console.rule(style="navy_blue")


    if not on_mobile:
        # To catch `Broken pipe` error
        try:
            from curl_cffi.curl import CurlError
        except ImportError:
            # curl_cffi not available (Termux/ARM), use fallback
            CurlError = Exception
    
    if global_settings_dict["captcha"]["toastOrPopup"] and not on_mobile and not misc_dict["hostMode"]:
        try:
            import tkinter as tk
            from tkinter import PhotoImage
            from queue import Queue
            
            popup_queue = Queue()

            main_bot_thread = threading.Thread(target=run_bots, args=(tokens_and_channels,))
            main_bot_thread.daemon = True
            main_bot_thread.start()

            popup_main_loop()
        except ImportError as e:
            print(f"⚠️ GUI features not available (tkinter not installed): {e}")
            print("Running in headless mode without popup notifications...")
            print("Tip: Set 'hostMode': true in config/misc.json to skip this check")
            run_bots(tokens_and_channels)
        except Exception as e:
            print(f"Error initializing GUI: {e}")
            print("Falling back to headless mode...")
            run_bots(tokens_and_channels)
    else:
        run_bots(tokens_and_channels)
