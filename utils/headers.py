import base64
import json
import re
import uuid
from datetime import datetime

import aiohttp

_DOLFIES = "https://cordapi.dolfi.es/api/v2/properties/web"
_LOGIN = "https://discord.com/login"
_CHROME_FEED = (
    "https://versionhistory.googleapis.com/v1/chrome/platforms/win/"
    "channels/stable/versions"
)
_SENTRY = re.compile(r"assets/(sentry\.\w+)\.js")
_BUILD = re.compile(r'buildNumber\D+(\d+)"')
_FALLBACK_BUILD = 307749
_FALLBACK_CHROME = 134


def _chrome_ua(major):
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{major}.0.0.0 Safari/537.36"
    )


async def _chrome_major(net):
    try:
        async with net.get(_CHROME_FEED, timeout=aiohttp.ClientTimeout(total=10)) as r:
            payload = await r.json()
        return int(payload["versions"][0]["version"].split(".")[0])
    except Exception:
        return _FALLBACK_CHROME


async def _build_number(net):
    probe = {
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": _LOGIN,
        "User-Agent": _chrome_ua(124),
    }
    try:
        async with net.get(_LOGIN, headers=probe) as r:
            shell = await r.text()
        sentry = _SENTRY.search(shell)
        if not sentry:
            return _FALLBACK_BUILD

        asset = f"https://static.discord.com/assets/{sentry.group(1)}.js"
        async with net.get(asset, headers=probe) as r:
            bundle = await r.text()
        hit = _BUILD.search(bundle)
        return int(hit.group(1)) if hit else _FALLBACK_BUILD
    except Exception:
        return _FALLBACK_BUILD


def _local_props(build, chrome):
    return {
        "os": "Windows",
        "browser": "Chrome",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": _chrome_ua(chrome),
        "browser_version": f"{chrome}.0.0.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": build,
        "client_event_source": None,
        "has_client_mods": False,
        "client_launch_id": str(uuid.uuid4()),
        "client_app_state": "unfocused",
        "client_heartbeat_session_id": str(uuid.uuid4()),
    }


def _encode(props):
    blob = json.dumps(props, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(blob).decode("utf-8")


async def _resolve_props(net):
    try:
        async with net.post(_DOLFIES) as r:
            payload = await r.json()
        props = payload.get("properties")
        encoded = payload.get("encoded")
        if props and encoded:
            return props, encoded
    except Exception:
        pass

    chrome = await _chrome_major(net)
    build = await _build_number(net)
    props = _local_props(build, chrome)
    return props, _encode(props)


async def generate_headers():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as net:
        props, encoded = await _resolve_props(net)

    locale = props.get("system_locale", "en-US")
    chrome = props.get("browser_version", "124")
    zone = datetime.now().astimezone().tzname() or "UTC"

    return {
        "accept": "*/*",
        "accept-language": f"{locale},en;q=0.5",
        "sec-ch-ua": f'"Not:A-Brand";v="24", "Chromium";v="{chrome}"',
        "sec-ch-ua-platform": f'"{props.get("os", "Windows")}"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-discord-locale": locale,
        "x-discord-timezone": zone,
        "x-super-properties": encoded,
        "origin": "https://discord.com",
        "x-debug-options": "bugReporterEnabled",
        "User-Agent": props.get("browser_user_agent", "Mozilla/5.0"),
        "Host": "discord.com",
        "Content-Type": "application/json",
        "Authorization": "",
        "Connection": "keep-alive",
        "Sec-GPC": "1",
        "Priority": "u=0",
        "TE": "trailers",
    }
