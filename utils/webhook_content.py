import json
import os

_CONTENT_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "webhookContent.json")

_cache = {}


def load_content(path=None):
    target = path if path else _CONTENT_PATH
    cache_key = os.path.abspath(target)
    if cache_key in _cache:
        return _cache[cache_key]
    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    _cache[cache_key] = data
    return data


def clear_cache():
    _cache.clear()


def get_template(key, path=None):
    content = load_content(path)
    template = content.get(key)
    return template if isinstance(template, dict) else {}


def render(text, values):
    if not isinstance(text, str):
        return text
    result = text
    for key, value in values.items():
        result = result.replace("{" + key + "}", str(value))
    return result
