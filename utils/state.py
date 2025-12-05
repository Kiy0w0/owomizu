"""
Shared state module for Mizu OwO Bot.
Stores global variables accessed by both the bot and the dashboard.
"""
import time

# Global variables
bot_instances = []
command_logs = []
website_logs = []
max_command_logs = 500
config_updated = False

# App start time
start_time = time.time()

# Active User IDs
list_user_ids = []

# Global Settings (loaded later)
settings = {}
misc = {}

