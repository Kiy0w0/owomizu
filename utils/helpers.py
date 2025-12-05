
import os
import sys
import socket
import datetime
import threading
from rich.console import Console
from rich.panel import Panel
from utils import state

# -- Global Console --
console = Console()
lock = threading.Lock()

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

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_weekday():
    # 0 = monday, 6 = sunday
    return str(datetime.datetime.today().weekday())

def get_hour():
    # only from 0 to 23 (24hr format)
    return datetime.datetime.now().hour

def get_date():
    return datetime.datetime.now().date().isoformat()  # e.g. "2025-05-31"

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

def printBox(text, color, title=None):
    test_panel = Panel(text, style=color, title=title)
    # Access state.misc if available, else default to False
    compact = False
    if state.misc and "console" in state.misc:
        compact = state.misc["console"].get("compactMode", False)
        
    if not compact:
        console.print(test_panel)
    else:
        console.print(text, style=color)

def merge_dicts(main, small):
    for key, value in small.items():
        if key in main and isinstance(main[key], dict) and isinstance(value, dict):
            merge_dicts(main[key], value)
        else:
            main[key] = value

def get_local_ip():
    # Check state.settings for config
    enable_host = False
    if state.settings and "website" in state.settings:
        enable_host = state.settings["website"].get("enableHost", False)

    if not enable_host:
        return 'localhost'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            """10.255.255.255 is fake"""
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
    except Exception:
        return 'localhost'
