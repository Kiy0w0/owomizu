import json
import os

_WATCHDOG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "watchdog.json")

_DEFAULTS = {
    "enabled": False,
    "stallMinutes": 15,
    "checkInterval": [60, 90],
}


def load_watchdog(path=None):
    target = path if path else _WATCHDOG_PATH
    try:
        with open(target, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(_DEFAULTS)
    if not isinstance(data, dict):
        return dict(_DEFAULTS)

    result = dict(_DEFAULTS)

    enabled = data.get("enabled", _DEFAULTS["enabled"])
    result["enabled"] = enabled if isinstance(enabled, bool) else _DEFAULTS["enabled"]

    stall = data.get("stallMinutes", _DEFAULTS["stallMinutes"])
    if isinstance(stall, bool) or not isinstance(stall, (int, float)) or stall <= 0:
        result["stallMinutes"] = _DEFAULTS["stallMinutes"]
    else:
        result["stallMinutes"] = stall

    interval = data.get("checkInterval", _DEFAULTS["checkInterval"])
    if (
        isinstance(interval, list)
        and len(interval) == 2
        and all(isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0 for v in interval)
        and interval[0] <= interval[1]
    ):
        result["checkInterval"] = interval
    else:
        result["checkInterval"] = _DEFAULTS["checkInterval"]

    return result


def is_paused(command_handler_status):
    s = command_handler_status
    if not s.get("state", True):
        return True
    return bool(
        s.get("captcha", False)
        or s.get("sleep", False)
        or s.get("hold_handler", False)
        or s.get("rate_limited", False)
    )


def is_stalled(last_ran, now, stall_seconds):
    if last_ran == 0:
        return False
    if stall_seconds <= 0:
        return False
    return (now - last_ran) > stall_seconds


def should_restart(command_handler_status, last_ran, now, cfg):
    if not cfg.get("enabled", False):
        return False
    if is_paused(command_handler_status):
        return False
    stall_secs = cfg.get("stallMinutes", _DEFAULTS["stallMinutes"]) * 60
    return is_stalled(last_ran, now, stall_secs)
