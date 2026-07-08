import json
import time

from flask import jsonify, request

AUTH_CONFIG_PATH = "config/auth_config.json"

LOCAL_ADDRESSES = {"127.0.0.1", "::1", "localhost"}

_failed_attempts = {}


def load_auth_config():
    try:
        with open(AUTH_CONFIG_PATH, "r") as config_file:
            return json.load(config_file)
    except (OSError, json.JSONDecodeError):
        return {}


def is_local_request():
    return request.remote_addr in LOCAL_ADDRESSES


def extract_code():
    if request.authorization and request.authorization.password:
        return request.authorization.password
    header_code = request.headers.get("X-Auth-Code")
    if header_code:
        return header_code
    return request.args.get("auth")


def challenge(message, status=401):
    response = jsonify({"status": "error", "message": message})
    response.status_code = status
    if status == 401:
        response.headers["WWW-Authenticate"] = 'Basic realm="Mizu Dashboard"'
    return response


def enforce_auth():
    config = load_auth_config()
    auth_settings = config.get("authentication", {})

    if not auth_settings.get("enabled", False):
        return None

    if is_local_request():
        return None

    web_access = config.get("web_access", {})
    if not web_access.get("allow_external", False):
        allowed_ips = set(web_access.get("allowed_ips", [])) | LOCAL_ADDRESSES
        if request.remote_addr not in allowed_ips:
            return challenge("External access is disabled", status=403)

    ip = request.remote_addr or "unknown"
    now = time.time()
    record = _failed_attempts.get(ip)

    if record and record["locked_until"] > now:
        return challenge("Too many failed attempts. Try again later.", status=403)

    expected = auth_settings.get("auth_code", "")
    if not expected:
        return challenge("Dashboard auth_code is not configured", status=403)

    provided = extract_code()
    if provided == expected:
        _failed_attempts.pop(ip, None)
        return None

    max_attempts = auth_settings.get("max_failed_attempts", 5)
    lockout = auth_settings.get("lockout_duration", 300)
    record = _failed_attempts.setdefault(ip, {"count": 0, "locked_until": 0})
    record["count"] += 1
    if record["count"] >= max_attempts:
        record["locked_until"] = now + lockout
        record["count"] = 0

    if provided is None:
        return challenge("Authentication required")
    return challenge("Invalid authentication code")
