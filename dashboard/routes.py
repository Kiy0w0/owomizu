# Standard Library
import json
import random
import time
import os
import sqlite3
import asyncio
from datetime import datetime

# Third-Party Libraries
from flask import jsonify, render_template, request
from . import app
from utils import state

# Helper Functions
def get_from_db(command):
    # This should be moved to a shared database utility in the future
    try:
        with sqlite3.connect("utils/data/db.sqlite") as conn:
            conn.row_factory = sqlite3.Row 
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL;")
            cur.execute(command)
            item = cur.fetchall()
            return item
    except Exception as e:
        print(f"Database error: {e}")
        return []

def load_global_settings():
    try:
        with open("config/global_settings.json", "r") as f:
            return json.load(f)
    except:
        return {}

def load_settings():
    try:
        with open("config/settings.json", "r") as f:
            return json.load(f)
    except:
        return {}

def merge_dicts(main, small):
    for key, value in small.items():
        if key in main and isinstance(main[key], dict) and isinstance(value, dict):
            merge_dicts(main[key], value)
        else:
            main[key] = value

def get_weekday():
    # Simple implementation, assuming 0-6
    return str(datetime.now().weekday())

version = "1.3.0"  # Ideally imported from main config

# Routes
@app.route("/")
def home():
    return render_template("index.html", version=version)

@app.route("/dashboard")
def dashboard():
    return render_template("index.html", version=version)

@app.route('/api/console', methods=['GET'])
def get_console_logs():
    global_settings = load_global_settings()

    try:
        log_string = '\n'.join(state.website_logs)
        return log_string
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return jsonify({"status": "error", "message": "An error occurred while fetching logs"}), 500

@app.route('/api/fetch_gamble_data', methods=['GET'])
def fetch_gamble_data():
    global_settings = load_global_settings()

    try:
        rows = get_from_db("SELECT hour, wins, losses FROM gamble_winrate ORDER BY hour")
        win_data = [row["wins"] for row in rows]
        lose_data = [row["losses"] for row in rows]
        return jsonify({
            "status": "success",
            "win_data": win_data,
            "lose_data": lose_data
        })
    except Exception as e:
        print(f"Error fetching gamble data: {e}")
        return jsonify({"status": "error", "message": "An error occurred"}), 500

@app.route('/api/fetch_cowoncy_data', methods=['GET'])
def fetch_cowoncy_data():
    global_settings = load_global_settings()


    try:
        rows = get_from_db("SELECT user_id, hour, earnings FROM cowoncy_earnings ORDER BY hour")
        user_data = {}
        for row in rows:
            user_id = row["user_id"]
            hour = row["hour"]
            earnings = row["earnings"]

            if user_id not in user_data:
                user_data[user_id] = {i: 0 for i in range(24)}
            user_data[user_id][hour] = earnings

        base_data = {
            "labels": [f"Hour {i}" for i in range(24)],
            "datasets": []
        }

        for user_id, hourly_data in user_data.items():
            color_hue = random.randint(0, 360)
            dataset = {
                "label": user_id,
                "data": [hourly_data[i] for i in range(24)],
                "borderColor": f"hsl({color_hue}, 100%, 50%)",
                "backgroundColor": f"hsl({color_hue}, 100%, 70%)",
                "fill": True,
                "tension": 0.4,
                "pointRadius": 0,
            }
            base_data["datasets"].append(dataset)

        rows = get_from_db("SELECT cowoncy, captchas FROM user_stats")
        total_cowoncy = sum(row["cowoncy"] for row in rows) if rows else 0
        total_captchas = sum(row["captchas"] for row in rows) if rows else 0

        return jsonify({
            "status": "success",
            "data": base_data,
            "total_cash": total_cowoncy,
            "total_captchas": total_captchas
        }), 200

    except Exception as e:
        print(f"Error fetching cowoncy data: {e}")
        return jsonify({"status": "error", "message": "An error occurred"}), 500

@app.route('/api/fetch_cmd_data', methods=['GET'])
def fetch_cmd_data():
    global_settings = load_global_settings()

    try:
        rows = get_from_db("SELECT * FROM commands")
        filtered_rows = [row for row in rows if row["count"] != 0]
        command_names = [row["name"] for row in filtered_rows]
        count = [row["count"] for row in filtered_rows]

        return jsonify({
            "status": "success",
            "command_names": command_names,
            "count": count
        })
    except Exception as e:
        print(f"Error fetching command data: {e}")
        return jsonify({"status": "error", "message": "An error occurred"}), 500

@app.route('/api/fetch_weekly_runtime', methods=['GET'])
def fetch_weekly_runtime():
    global_settings = load_global_settings()

    try:
        with open("utils/data/weekly_runtime.json", "r") as config_file:
            data_dict = json.load(config_file)
        
        runtime_data = [(val[1] - val[0]) / 60 for val in data_dict.values() if isinstance(val, list)]
        cur_hour = get_weekday()

        return jsonify({
            "status": "success",
            "runtime_data": runtime_data,
            "current_uptime": data_dict.get(cur_hour, [0,0])
        })
    except Exception as e:
        print(f"Error fetching weekly runtime: {e}")
        return jsonify({"status": "error", "message": "An error occurred"}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        return jsonify(load_settings())
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch settings"}), 500

@app.route('/api/dashboard/status', methods=['GET'])
def get_dashboard_status():
    try:
        # Simple status based on active user IDs from loaded bot instances
        # Need to access global listUserIds if possible, or infer from bot_instances
        active_accounts = len(state.bot_instances)
        
        captcha_status = False
        sleep_status = False
        
        for bot_instance in state.bot_instances:
            if hasattr(bot_instance, 'command_handler_status'):
                if bot_instance.command_handler_status.get("captcha", False):
                    captcha_status = True
                if bot_instance.command_handler_status.get("sleep", False):
                    sleep_status = True
                    
        if active_accounts > 0:
            if captcha_status:
                bot_status = "captcha"
            elif sleep_status:
                bot_status = "paused"
            else:
                bot_status = "online"
        else:
            bot_status = "offline"
        
        # Total accounts estimate
        try:
           with open("tokens.txt", "r") as f:
               total_accounts = len(f.readlines())
        except:
            total_accounts = 0

        return jsonify({
            "status": bot_status,
            "active_accounts": active_accounts,
            "total_accounts": total_accounts,
            "captcha_detected": captcha_status,
            "is_sleeping": sleep_status,
            "timestamp": time.time()
        })
    except Exception as e:
        print(f"Error fetching dashboard status: {e}")
        return jsonify({
            "status": "error",
            "active_accounts": 0,
            "total_accounts": 0,
            "captcha_detected": False,
            "is_sleeping": False,
            "timestamp": time.time()
        }), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        stats_data = {
            "balance": 0,
            "hunts_today": 0,
            "battles_today": 0,
            "uptime": 0,
            "commands_executed": 0,
            "captchas_solved": 0,
            "accounts": []
        }
        
        # Get data from database
        try:
            account_rows = get_from_db("SELECT user_id, cowoncy, captchas FROM user_stats")
            total_cowoncy = 0
            total_captchas = 0
            
            for row in account_rows:
                user_id = row["user_id"]
                cowoncy = row["cowoncy"] or 0
                captchas = row["captchas"] or 0
                
                total_cowoncy += cowoncy
                total_captchas += captchas
                
                user_display = f"User-{str(user_id)[-4:]}"
                
                stats_data["accounts"].append({
                    "user_id": user_id,
                    "user_display": user_display,
                    "cowoncy": cowoncy,
                    "cowoncy_formatted": f"{cowoncy:,}",
                    "captchas": captchas
                })
            
            stats_data["balance"] = total_cowoncy
            stats_data["balance_formatted"] = f"{total_cowoncy:,}"
            stats_data["captchas_solved"] = total_captchas
            
            hunt_rows = get_from_db("SELECT count FROM commands WHERE name = 'hunt'")
            battle_rows = get_from_db("SELECT count FROM commands WHERE name = 'battle'")
            
            stats_data["hunts_today"] = hunt_rows[0]["count"] if hunt_rows else 0
            stats_data["battles_today"] = battle_rows[0]["count"] if battle_rows else 0
            
            all_commands = get_from_db("SELECT SUM(count) as total FROM commands")
            stats_data["commands_executed"] = all_commands[0]["total"] if all_commands and all_commands[0]["total"] else 0
            
        except Exception as db_error:
            print(f"Database error in dashboard stats: {db_error}")
        
        if hasattr(state, 'start_time'):
            stats_data["uptime"] = int(time.time() - state.start_time)
        
        return jsonify(stats_data)
        
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return jsonify({
            "balance": 0,
            "hunts_today": 0,
            "battles_today": 0,
            "uptime": 0,
            "commands_executed": 0,
            "captchas_solved": 0
        })

@app.route('/api/dashboard/logs', methods=['GET'])
def get_dashboard_logs():
    try:
        recent_logs = state.website_logs[-100:] if len(state.website_logs) > 100 else state.website_logs
        formatted_logs = []
        for i, log in enumerate(recent_logs):
            level = "info"
            if "error" in log.lower() or "failed" in log.lower():
                level = "error"
            elif "warning" in log.lower() or "captcha" in log.lower():
                level = "warning"
            elif "success" in log.lower() or "completed" in log.lower() or "won" in log.lower():
                level = "success"
            
            formatted_logs.append({
                "id": i,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "level": level,
                "message": log
            })
        return jsonify(formatted_logs)
    except Exception as e:
        print(f"Error fetching dashboard logs: {e}")
        return jsonify([])

@app.route('/api/dashboard/activity', methods=['GET'])
def get_dashboard_activity():
    try:
        activities = []
        try:
            recent_commands = get_from_db("""
                SELECT name, count, MAX(rowid) as latest 
                FROM commands 
                WHERE count > 0 
                GROUP BY name 
                ORDER BY latest DESC 
                LIMIT 10
            """)
            
            for cmd in recent_commands:
                activities.append({
                    "time": "Recently",
                    "message": f"{cmd['name'].title()} command executed {cmd['count']} times",
                    "type": "info",
                    "icon": "fas fa-terminal"
                })
        except Exception as db_error:
            print(f"Database error in activity: {db_error}")
            
        recent_website_logs = state.website_logs[-5:] if state.website_logs else []
        for log in recent_website_logs:
            activity_type = "info"
            icon = "fas fa-info-circle"
            if "hunt" in log.lower():
                activity_type = "success"
                icon = "fas fa-paw"
            elif "battle" in log.lower():
                activity_type = "success" 
                icon = "fas fa-sword"
            elif "captcha" in log.lower():
                activity_type = "warning"
                icon = "fas fa-exclamation-triangle"
            elif "error" in log.lower():
                activity_type = "error"
                icon = "fas fa-exclamation-circle"
                
            activities.append({
                "time": "Just now",
                "message": log,
                "type": activity_type,
                "icon": icon
            })
        
        return jsonify(activities[-10:])
    except Exception as e:
        print(f"Error fetching dashboard activity: {e}")
        return jsonify([])

@app.route('/api/dashboard/analytics', methods=['GET'])
def get_dashboard_analytics():
    try:
        now_ts = time.time()
        one_min_ago = now_ts - 60
        active_accounts = {}
        
        try:
            for client in state.bot_instances:
                if hasattr(client, 'user') and client.user:
                    acc_id = str(client.user.id)
                    active_accounts[acc_id] = {
                        "account_id": acc_id,
                        "account_display": getattr(client, 'username', None) or getattr(getattr(client, 'user', None), 'name', None) or f"User-{acc_id[-4:]}",
                        "active": True,
                        "net_earnings": getattr(client, 'user_status', {}).get('net_earnings', 0)
                    }
        except Exception:
            pass

        for log in state.command_logs:
            acc_id = log.get('account_id')
            if not acc_id:
                continue
            active_accounts.setdefault(acc_id, {
                "account_id": acc_id,
                "account_display": log.get('account_display') or f"User-{acc_id[-4:]}",
                "active": False,
                "net_earnings": 0
            })

        for acc in active_accounts.values():
            acc.update({
                "cpm": 0,
                "session_total": 0,
                "hunt": 0,
                "battle": 0,
                "daily": 0,
                "owo": 0,
                "last_command_ts": None
            })

        global_cpm = 0
        for log in state.command_logs:
            ts = log.get('timestamp', 0)
            if ts >= one_min_ago:
                global_cpm += 1
            acc_id = log.get('account_id')
            if acc_id in active_accounts:
                acc = active_accounts[acc_id]
                acc['session_total'] += 1
                if ts >= one_min_ago:
                    acc['cpm'] += 1
                ctype = (log.get('command_type') or '').lower()
                if 'hunt' in ctype:
                    acc['hunt'] += 1
                elif 'battle' in ctype:
                    acc['battle'] += 1
                elif 'daily' in ctype:
                    acc['daily'] += 1
                elif ctype in {'owo', 'uwu'} or 'owo' in ctype:
                    acc['owo'] += 1
                if ts and (not acc['last_command_ts'] or ts > acc['last_command_ts']):
                    acc['last_command_ts'] = ts

        global_session_total = sum(a['session_total'] for a in active_accounts.values())
        global_net = sum(a.get('net_earnings', 0) for a in active_accounts.values())

        return jsonify({
            "global": {
                "cpm": global_cpm,
                "active_accounts": sum(1 for a in active_accounts.values() if a['active']),
                "session_total": global_session_total,
                "net_earnings": global_net,
                "timestamp": now_ts
            },
            "accounts": list(active_accounts.values())
        })
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return jsonify({"global": {"cpm": 0, "active_accounts": 0, "session_total": 0, "net_earnings": 0}, "accounts": []})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        new_settings = request.get_json()
        current_settings = load_settings() 
        merge_dicts(current_settings, new_settings)
        
        with open("config/settings.json", "w") as config_file:
            json.dump(current_settings, config_file, indent=4)
        
        state.config_updated = True
        return jsonify({"status": "success", "message": "Settings updated successfully"})
    except Exception as e:
        print(f"Error updating settings: {e}")
        return jsonify({"status": "error", "message": "Failed to update settings"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats_data = {}
        try:
            rows = get_from_db("SELECT cowoncy FROM user_stats")
            total_cowoncy = sum(row["cowoncy"] for row in rows) if rows else 0
            stats_data["balance"] = total_cowoncy
        except:
            stats_data["balance"] = 0
        
        try:
            rows = get_from_db("SELECT count FROM commands WHERE name = 'hunt'")
            hunt_count = rows[0]["count"] if rows else 0
            stats_data["hunts_today"] = hunt_count
        except:
            stats_data["hunts_today"] = 0
        
        try:
            rows = get_from_db("SELECT count FROM commands WHERE name = 'battle'")
            battle_count = rows[0]["count"] if rows else 0
            stats_data["battles_today"] = battle_count
        except:
            stats_data["battles_today"] = 0
        
        stats_data["uptime"] = int(time.time() % 86400) # Simplified
        return jsonify(stats_data)
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch stats"}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        recent_logs = state.website_logs[-50:] if len(state.website_logs) > 50 else state.website_logs
        formatted_logs = []
        for i, log in enumerate(recent_logs):
            formatted_logs.append({
                "id": i,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "level": "info",
                "message": log
            })
        return jsonify(formatted_logs)
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return jsonify([])

@app.route('/api/dashboard/quick-toggle', methods=['POST'])
def toggle_quick_setting():
    try:
        data = request.get_json()
        command = data.get('command')
        enabled = data.get('enabled')
        
        if command not in ['hunt', 'battle', 'daily', 'owo', 'channelSwitcher', 'useSlashCommands', 'stopHuntingWhenNoGems']:
            return jsonify({"status": "error", "message": "Invalid command"}), 400
            
        # Update settings file
        settings = load_settings()
        
        if command == 'channelSwitcher':
            if 'channelSwitcher' not in settings:
                settings['channelSwitcher'] = {}
            settings['channelSwitcher']['enabled'] = enabled
            
        elif command == 'useSlashCommands':
            settings['useSlashCommands'] = enabled
            
        elif command == 'stopHuntingWhenNoGems':
            settings['stopHuntingWhenNoGems'] = enabled
            
        else:
            # Command toggles
            if command not in settings['commands']:
                settings['commands'][command] = {}
            settings['commands'][command]['enabled'] = enabled
            
        # Save settings
        with open("config/settings.json", "w") as f:
            json.dump(settings, f, indent=4)
            
        # Trigger update in running bots
        # In this refactored version, we rely on the bot polling config_updated or similar mechanism
        # But we also have refresh_bot_settings logic in mizu.py. 
        # Since we moved routes here, we can't directly call mizu.py functions easily without circular imports.
        # Ideally, we set a flag in shared state.
        state.config_updated = True
            
        # Also try to apply immediately if we have access to bot instances
        # This part requires re-implementing refresh_bot_settings logic here or making it shared.
        # For now, let's just use the state flag.
        
        # If we want to emulate the original behavior of immediate application:
        # We can iterate through state.bot_instances and call their method if they are Objects
        # However, calling async methods from Flask sync route requires a new loop or run_coroutine_threadsafe.
        # For simplicity in this step, we just rely on state flag.
        
        # Advanced: Try to trigger immediate update if possible
        if state.bot_instances:
            loop = asyncio.get_event_loop_policy().get_event_loop() # This might not work if loop is in another thread
            # Skipping complex async interaction for now to keep refactor safe.
            pass

        return jsonify({"status": "success", "message": f"{command} toggled successfully"})
        
    except Exception as e:
        print(f"Error toggling setting: {e}")
        return jsonify({"status": "error", "message": f"Failed to toggle {command}"}), 500
