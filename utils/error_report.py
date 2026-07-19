import re
import time
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import aiohttp

from utils.webhook import DiscordWebhook

_WINDOWS_HOME = re.compile(r"[A-Za-z]:\\Users\\[^\\\"'/\s]+", re.IGNORECASE)
_UNIX_HOME = re.compile(r"/(?:home|Users)/[^/\"'\s]+", re.IGNORECASE)
_WEBHOOK_URL = re.compile(
    r"https?://(?:\w+\.)?discord(?:app)?\.com/api/webhooks/\S+", re.IGNORECASE
)
_DISCORD_TOKEN = re.compile(r"[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{20,}")

_REDACTED = "[REDACTED]"


def sanitize_traceback(text, enabled=True, max_length=1500):
    if not isinstance(text, str):
        return text
    if not enabled:
        return text

    result = _WEBHOOK_URL.sub(_REDACTED, text)
    result = _DISCORD_TOKEN.sub(_REDACTED, result)
    result = _WINDOWS_HOME.sub("~", result)
    result = _UNIX_HOME.sub("~", result)

    if len(result) > max_length:
        result = result[:max_length]
    return result


def build_report_payload(error_type, message, traceback_text, account_name, version):
    return {
        "error_type": error_type,
        "message": message,
        "traceback": traceback_text,
        "account": account_name,
        "version": version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


class ErrorReporter:

    def __init__(self, config: Dict[str, Any], account_name: str = "unknown", version: str = ""):
        self.config = config or {}
        self.account_name = account_name
        self.version = version
        self.enabled = self.config.get("enabled", False)
        self.mode = self.config.get("mode", "relay")
        self.user_webhook_url = self.config.get("userWebhookUrl", "")
        self.relay_url = self.config.get("relayUrl", "")
        self.relay_secret = self.config.get("relaySecret", "")
        self.sanitize = self.config.get("sanitize", True)
        self.max_per_minute = self.config.get("maxPerMinute", 5)

        self._seen = set()
        self._send_times = []
        self._direct_hook = None
        self._session = None

    def _get_direct_hook(self):
        if self._direct_hook is None:
            self._direct_hook = DiscordWebhook(self.user_webhook_url)
        return self._direct_hook

    def _fingerprint(self, error_type, message):
        raw = f"{error_type}|{message}".encode("utf-8", "replace")
        return hashlib.sha1(raw).hexdigest()

    def _rate_limited(self):
        now = time.monotonic()
        self._send_times = [t for t in self._send_times if now - t < 60]
        if len(self._send_times) >= self.max_per_minute:
            return True
        self._send_times.append(now)
        return False

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _post_relay(self, url, payload, secret):
        try:
            session = await self._get_session()
            headers = {"X-Mizu-Secret": secret} if secret else {}
            async with session.post(url, json=payload, headers=headers) as resp:
                return resp.status in (200, 201, 202, 204)
        except Exception:
            return False

    def _transport(self, payload):
        return None

    async def report(self, error_type, message, traceback_text):
        if not self.enabled:
            return False

        fingerprint = self._fingerprint(error_type, message)
        if fingerprint in self._seen:
            return False

        if self._rate_limited():
            return False

        self._seen.add(fingerprint)

        tb = sanitize_traceback(traceback_text, enabled=self.sanitize)
        clean_message = sanitize_traceback(message, enabled=self.sanitize, max_length=500)

        if self.mode == "direct":
            if not self.user_webhook_url:
                return False
            hook = self._get_direct_hook()
            await hook.send_error(
                account_name=self.account_name,
                error_type=error_type,
                error_message=clean_message,
                traceback=tb,
            )
            return True

        if not self.relay_url:
            return False

        payload = build_report_payload(
            error_type=error_type,
            message=clean_message,
            traceback_text=tb,
            account_name=self.account_name,
            version=self.version,
        )
        return await self._post_relay(self.relay_url, payload, self.relay_secret)

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
        if self._direct_hook:
            await self._direct_hook.close()
