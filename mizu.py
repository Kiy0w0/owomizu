# Standard Library
import asyncio
import itertools
import json
import logging
import logging.handlers
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
from utils import helpers
from utils.helpers import compare_versions, printBox, resource_path, get_weekday, get_hour, get_date, get_local_ip, console, lock
from utils.state import list_user_ids as listUserIds
from bot.client import MyClient
from dashboard import create_app

app = create_app() # Initialize Flask app

def run_flask():
    try:
        if global_settings_dict["website"]["enabled"]:
             # Suppress Flask logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            app.run(host='0.0.0.0', port=global_settings_dict["website"]["port"])
    except Exception as e:
        print(f"Error starting Flask: {e}")

"""Cntrl+c detect"""
def handle_sigint(signal_number, frame):
    print("\nCtrl+C detected. Initiating graceful shutdown...")
    
    # Attempt to close all active bot instances
    for client in state.bot_instances:
        try:
            if client.loop.is_running():
                # Schedule client.close() in the client's event loop
                asyncio.run_coroutine_threadsafe(client.close(), client.loop)
        except Exception as e:
            print(f"Error closing client: {e}")
            
    print("Waiting for connections to close...")
    time.sleep(1.5) # Give asyncio time to clean up SSL transports
    print("Exiting.")
    os._exit(0)

signal.signal(signal.SIGINT, handle_sigint)

def setup_logging():
    handler = logging.handlers.RotatingFileHandler(
        filename='logs.txt',
        encoding='utf-8',
        maxBytes=5 * 1024 * 1024,  # 5 MiB
        backupCount=3,
    )
    formatter = logging.Formatter('[{asctime}] {name} - {message}', style='{')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger("bot")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)




def clear():
    os.system('cls') if os.name == 'nt' else os.system('clear')

console = helpers.console
lock = helpers.lock
clear()


def load_accounts_dict(file_path="utils/stats.json"):
    with open(file_path, "r") as config_file:
        return json.load(config_file)

with open("config/global_settings.json", "r") as config_file:
    global_settings_dict = json.load(config_file)
    state.settings = global_settings_dict

with open("config/misc.json", "r") as config_file:
    misc_dict = json.load(config_file)
    state.misc = misc_dict


console.rule("[bold blue1]:>", style="navy_blue")
console_width = console.size.width
# listUserIds imported from state


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
version = "1.4.0"
debug_print = True

def merge_dicts(main, small):
    for key, value in small.items():
        if key in main and isinstance(main[key], dict) and isinstance(value, dict):
            merge_dicts(main[key], value)
        else:
            main[key] = value



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


# Legacy routes removed. All routes are now in dashboard/routes.py



""""""





# Note: is_termux() and on_mobile already defined at the top of the file (line 22-33)

if not on_mobile and not misc_dict["hostMode"]:
    try:
        if global_settings_dict["batteryCheck"]["enabled"]:
            import psutil
    except Exception as e:
        print(f"ImportError: {e}")


# For time related stuff



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


# MyClient logic moved to bot/client.py

# get_local_ip moved to utils.helpers


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

                except Exception as e:
                    # Check for CurlError if defined (imported in main)
                    if 'CurlError' in globals() and isinstance(e, globals()['CurlError']):
                         if "WS_SEND" in str(e) and "55" in str(e):
                            printBox("Broken pipe error detected. Restarting bot...", "bold red")
                            if client in state.bot_instances: state.bot_instances.remove(client)
                            continue 
                         else:
                            printBox(f"Curl error: {e}", "bold red")
                            if client in state.bot_instances: state.bot_instances.remove(client)
                            break
                    
                    printBox(f"Unknown error when running bot: {e}", "bold red")
                    if client in state.bot_instances: state.bot_instances.remove(client)

            else:
                # Mobile (Termux) uses an older version without curl_cffi.
                try:
                    client.run(token, log_level=logging.ERROR)
                except Exception as e:
                    printBox(f"Unknown error when running bot: {e}", "bold red")
                finally:
                    if client in state.bot_instances: state.bot_instances.remove(client)
                break 
            
            # Ensure removal if loop continues naturally
            if client in state.bot_instances:
                state.bot_instances.remove(client)
            
            if getattr(client, "should_exit", False):
                break

    except Exception as e:
        printBox(f"Error starting bot: {e}", "bold red")

def stop_batch(active_clients):
    """Gracefully stop a batch of clients"""
    printBox(f"Stopping batch of {len(active_clients)} bots...", "bold yellow")
    for client in active_clients:
        try:
            if client.loop.is_running():
                asyncio.run_coroutine_threadsafe(client.close(), client.loop)
        except Exception as e:
            print(f"Error closing client: {e}")
            
    # Wait for them to actually close
    time.sleep(5)
    
    # Clean up state
    for client in active_clients:
        if client in state.bot_instances:
            state.bot_instances.remove(client)

def run_rotation_mode(tokens_and_channels):
    """Run bots in rotation/shift mode"""
    rotation_config = global_settings_dict["accountRotation"]
    batch_size = rotation_config["accountsPerShift"]
    shift_duration = rotation_config["shiftDurationMinutes"] * 60
    cooldown = rotation_config["cooldownBetweenShiftsSeconds"]
    
    # Create batches
    batches = [tokens_and_channels[i:i + batch_size] for i in range(0, len(tokens_and_channels), batch_size)]
    total_batches = len(batches)
    
    if total_batches == 0:
        printBox("No tokens to rotate!", "bold red")
        return

    printBox(f"Rotation Mode: {total_batches} batches found. Shift duration: {rotation_config['shiftDurationMinutes']}m", "bold cyan")
    
    while True:
        for i, batch in enumerate(batches):
            printBox(f"Starting Batch {i+1}/{total_batches}", "bold green")
            
            # Start the threads for this batch
            batch_threads = []
            for token, channel_id in batch:
                thread = Thread(target=run_bot, args=(token, channel_id, global_settings_dict))
                thread.start()
                batch_threads.append(thread)
            
            # Wait for the shift duration
            # Check every second to allow quick exit on Ctrl+C
            end_time = time.time() + shift_duration
            while time.time() < end_time:
                time.sleep(1)
            
            # Stop the current batch
            # We need to find which clients correspond to this batch
            # Actually, we can just stop ALL active clients since we only run one batch at a time
            # But to be safe, we close all in state.bot_instances
            
            active_clients = list(state.bot_instances) # Create copy
            stop_batch(active_clients)
            
            # Join threads to ensure they are cleaned up
            for t in batch_threads:
                t.join(timeout=5)
                
            printBox(f"Batch {i+1} finished. Cooling down for {cooldown}s...", "bold blue")
            time.sleep(cooldown)

if __name__ == "__main__":
    setup_logging()
    # Version check disabled to prevent reinstall loop
    if not misc_dict["console"]["compactMode"]:
        console.print(mizuPanel)
        console.rule(f"[bold blue1]version - {version}", style="navy_blue")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Try loading tokens from environment variable first
    tokens_env = os.getenv("TOKENS")
    if tokens_env:
        # Format: "token1 channel1;token2 channel2"
        raw_tokens = [entry.strip().split() for entry in tokens_env.split(';') if entry.strip()]
        tokens_and_channels = []
        for t in raw_tokens:
            if len(t) >= 2:
                tokens_and_channels.append(t[:2])
            elif len(t) == 1:
                # Handle case where user provided token but no channel
                # We can append a default channel '0' or skip. Let's append '0' to avoid crash but warn user
                print(f"Warning: Token ending in ...{t[0][-5:]} is missing Channel ID. Defaulting to 0.")
                tokens_and_channels.append([t[0], "0"])
        
        printBox("Loaded tokens from .env file", "bold green")
    elif os.path.exists("tokens.txt"):
        tokens_and_channels = []
        for line in open("tokens.txt", "r"):
            parts = line.strip().split()
            if len(parts) >= 2:
                tokens_and_channels.append(parts[:2])
            elif len(parts) == 1:
                 tokens_and_channels.append([parts[0], "0"])
        printBox(f"WARNING: Using tokens.txt is deprecated. Please migrate to .env", "bold yellow")
    else:
        printBox("No tokens found! Check .env or tokens.txt", "bold red")
        tokens_and_channels = []

    token_len = len(tokens_and_channels)

    printBox(f'-Received {token_len} tokens.'.center(console_width - 2 ),'bold cyan' )

    # Create database or modify if required
    create_database()

    # Weekly runtime thread
    start_runtime_loop()

    if global_settings_dict["website"]["enabled"]:
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
    
    # Start Flask thread (Always run dashboard)
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

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
            if global_settings_dict["accountRotation"]["enabled"]:
                run_rotation_mode(tokens_and_channels)
            else:
                run_bots(tokens_and_channels)
    else:
        if global_settings_dict["accountRotation"]["enabled"]:
            run_rotation_mode(tokens_and_channels)
        else:
            run_bots(tokens_and_channels)
