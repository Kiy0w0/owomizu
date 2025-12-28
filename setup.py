
import os
import json
import time
import sys
import subprocess
import shutil

# Color codes
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
RESET = "\033[m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def is_termux():
    return os.path.isdir("/data/data/com.termux")

def install_dependencies():
    print(f"{CYAN}[0] Checking dependencies...{RESET}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Termux specific
        if is_termux():
            print(f"{CYAN}[0] Installing Termux specific dependencies...{RESET}")
            try:
                subprocess.check_call(["pkg", "install", "python-numpy", "python-pillow", "termux-api", "-y"])
            except:
                pass
                
        print(f"{GREEN}[✓] Dependencies installed!{RESET}\n")
    except Exception as e:
        print(f"{RED}[!] Error installing dependencies: {e}{RESET}")
        print(f"{YELLOW}Continuing anyway...{RESET}\n")

def print_banner():
    clear()
    print(f"{CYAN}")
    print(r"""
  ███╗   ███╗██╗███████╗██╗   ██╗
  ████╗ ████║██║╚══███╔╝██║   ██║
  ██╔████╔██║██║  ███╔╝ ██║   ██║  
  ██║╚██╔╝██║██║ ███╔╝  ██║   ██║ 
  ██║ ╚═╝ ██║██║███████╗╚██████╔╝ 
  ╚═╝     ╚═╝╚═╝╚══════╝ ╚═════╝ 
 M I Z U   N E T W O R K   水
    """)
    print(f"{RESET}")
    print(f"{GREEN}Interactive Setup Wizard{RESET}\n")

def main():
    print_banner()
    print("Welcome to Mizu OwO Setup!")
    print("This wizard will help you configure your bot quickly.\n")
    
    # 0. Dependencies
    install_dependencies()

    # 1. Token Setup
    print(f"{YELLOW}[1] Account Setup{RESET}")
    tokens = []
    while True:
        token = input("Enter your Discord Token: ").strip().replace('"', '')
        
        while True:
            try:
                channel_id = input("Enter Channel ID for Farming: ").strip()
                int(channel_id) # Validate integer
                break
            except ValueError:
                print(f"{RED}Invalid Channel ID! Please enter numbers only.{RESET}")

        tokens.append(f"{token} {channel_id}")
        
        more = input("Add another account? (y/n): ").lower()
        if more != 'y':
            break
    
    # Save to .env
    with open(".env", "w") as f:
        f.write('TOKENS="' + ";".join(tokens) + '"\n')
    print(f"{GREEN}Checking... Accounts saved to .env!{RESET}\n")

    # 2. Configuration Profile
    print(f"{YELLOW}[2] Behavior Profile{RESET}")
    print("Choose a farming style:")
    print("1. Safe (Recommended) - Slower, human-like, low ban risk")
    print("2. Aggressive - Fast, max profit, higher ban risk")
    print("3. Custom - Keep existing settings (if any)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice in ['1', '2']:
        base_settings = {
            "setprefix": "owo ",
            "useSlashCommands": False,
            "commands": {
                "hunt": {"enabled": True, "cooldown": [15, 20], "useShortForm": True},
                "battle": {"enabled": True, "cooldown": [15, 20], "useShortForm": True},
                "sell": {"enabled": False, "cooldown": [410, 500], "rarity": ["c", "u", "r"]},
                "sac": {"enabled": False, "cooldown": [410, 500], "rarity": ["c", "u", "r"]},
                "pray": {"enabled": False, "cooldown": [310, 400], "userid": [], "pingUser": False},
                "curse": {"enabled": False, "cooldown": [310, 400], "userid": [], "pingUser": False},
                "lottery": {"enabled": False, "amount": 1},
                "lvlGrind": {"enabled": False, "cooldown": [10, 15], "useQuoteInstead": False},
                "cookie": {"enabled": False, "userid": 0, "pingUser": False},
                "shop": {"enabled": False, "itemsToBuy": [1], "cooldown": [10, 16]},
                "owo": {"enabled": True, "cooldown": [10, 15]},
                "autoHuntBot": {"enabled": True, "cashToSpend": 10000, "upgrader": {"enabled": True, "sleeptime": [10, 15], "priorities": {"efficiency": 4, "duration": 2, "cost": 5, "gain": 4, "exp": 3, "radar": 1}}}
            },
            "gamble": {
                "allottedAmount": 0,
                "goalSystem": {"enabled": False, "amount": 0},
                "coinflip": {"enabled": False, "startValue": 0, "multiplierOnLose": 0, "cooldown": [15, 20], "options": ["h"]},
                "slots": {"enabled": False, "startValue": 0, "multiplierOnLose": 0, "cooldown": [15, 20]},
                "blackjack": {}
            },
            "giveawayJoiner": {"enabled": False, "channelsToJoin": [], "cooldown": [40, 100], "messageRangeToCheck": 6},
            "sleep": {"enabled": True, "frequencyPercentage": 50, "checkTime": [10, 20], "sleeptime": [300, 600]},
             "misspell": {
                "enabled": True,
                "frequencyPercentage": 1,
                "baseDelay": [0.03, 0.07],
                "errorRectificationTimePerLetter": [0.04, 0.09]
            },
            "autoDaily": True,
            "cashCheck": True,
            "defaultCooldowns": {
                 "longCooldown": [400, 600],
                 "moderateCooldown": [70, 200],
                 "shortCooldown": [10, 60],
                 "briefCooldown": [1, 3],
                 "captchaRestart": [5, 10],
                 "commandHandler": {"betweenCommands": [2, 4], "beforeReaddingToQueue": 7},
                 "reactionBot": {"hunt_and_battle": True, "owo": False, "pray_and_curse": False, "cooldown": [1, 2]}
            },
            "richPresence": {
                "enabled": True,
                "mode": "ninja",
                "status": "online",
                "activityType": "playing",
                "text": "Visual Studio Code"
            }
        }

        if choice == '1': # Safe
            print(f"{GREEN}Applying Safe Profile...{RESET}")
            # Safe defaults already set above essentially, just ensuring long delays
            base_settings["sleep"]["enabled"] = True
            base_settings["misspell"]["enabled"] = True
            base_settings["defaultCooldowns"]["commandHandler"]["betweenCommands"] = [3, 6]
            
        elif choice == '2': # Aggressive
            print(f"{RED}Applying Aggressive Profile...{RESET}")
            base_settings["commands"]["hunt"]["cooldown"] = [15, 16]
            base_settings["commands"]["battle"]["cooldown"] = [15, 16]
            base_settings["commands"]["owo"]["cooldown"] = [10, 12]
            base_settings["defaultCooldowns"]["commandHandler"]["betweenCommands"] = [0.5, 1.5]
            base_settings["sleep"]["enabled"] = False # No sleep for the wicked
            base_settings["misspell"]["enabled"] = False
            
        # Ensure directory
        if not os.path.exists("config"):
            os.makedirs("config")
            
        # Save config
        with open("config/settings.json", "w") as f:
            json.dump(base_settings, f, indent=4)
        print(f"{GREEN}Configuration saved to config/settings.json!{RESET}\n")

    # 3. Finalize
    print(f"{CYAN}Setup Complete!{RESET}")
    print("You can now run the bot using:")
    print(f"{GREEN}python mizu.py{RESET}")

if __name__ == "__main__":
    main()
