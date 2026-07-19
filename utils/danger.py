import json
import os

_DANGER_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "danger.json")

_DEFAULTS = {
    "allowAutoQuest": False,
    "allowLevelQuotes": False,
    "allowChannelSwitcher": False,
}


def load_danger(path=None):
    target = path if path else _DANGER_PATH
    try:
        with open(target, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(_DEFAULTS)
    if not isinstance(data, dict):
        return dict(_DEFAULTS)
    merged = dict(_DEFAULTS)
    for key in _DEFAULTS:
        value = data.get(key, _DEFAULTS[key])
        merged[key] = value if isinstance(value, bool) else _DEFAULTS[key]
    return merged


def is_allowed(gate, danger_dict=None):
    if gate not in _DEFAULTS:
        return False
    source = danger_dict if isinstance(danger_dict, dict) else load_danger()
    value = source.get(gate, False)
    return value is True
