import asyncio
import json

import aiohttp
import requests

_YC_BASE = "https://api.yescaptcha.com"
_OWO_SITE_KEY = "a6a1d5ce-612d-472d-8e37-7601408fbc09"
_OWO_CLIENT_ID = "408785106942164992"
_SOFT_ID = 94493
_MIN_CREDIT = 30
_POLL_LIMIT = 60
_POLL_GAP = 2


class HCaptchaSolver:
    def __init__(self, api_key):
        self.api_key = api_key
        self.balance = self._read_balance()
        self._oauth_endpoint = (
            "https://discord.com/api/v9/oauth2/authorize"
            f"?client_id={_OWO_CLIENT_ID}&response_type=code"
            "&redirect_uri=https://owobot.com/api/auth/discord/redirect"
            "&scope=identify guilds"
        )
        self._oauth_body = {
            "authorize": True,
            "integration_type": 0,
            "permissions": "0",
            "location_context": {
                "guild_id": "10000",
                "channel_id": "10000",
                "channel_type": 10000,
            },
        }

    def _read_balance(self):
        try:
            reply = requests.post(
                f"{_YC_BASE}/getBalance",
                json={"clientKey": self.api_key},
                timeout=10,
            ).json()
        except Exception:
            return 0
        if reply.get("errorId") != 0:
            return 0
        return int(reply.get("balance", 0))

    def refresh(self):
        self.balance = self._read_balance()

    async def _request_token(self, retries):
        body = {
            "clientKey": self.api_key,
            "task": {
                "type": "HCaptchaTaskProxyless",
                "websiteKey": _OWO_SITE_KEY,
                "websiteURL": "https://owobot.com",
            },
            "softID": _SOFT_ID,
        }

        async with aiohttp.ClientSession() as net:
            attempt = 0
            while attempt < retries:
                attempt += 1
                try:
                    async with net.post(f"{_YC_BASE}/createTask", json=body) as r:
                        created = await r.json() if r.status == 200 else None
                    if not created or created.get("errorId") != 0:
                        raise RuntimeError("task creation rejected")

                    ticket = created.get("taskId")
                    if not ticket:
                        raise RuntimeError("missing taskId")

                    for _ in range(_POLL_LIMIT):
                        await asyncio.sleep(_POLL_GAP)
                        async with net.post(
                            f"{_YC_BASE}/getTaskResult",
                            json={"clientKey": self.api_key, "taskId": ticket},
                        ) as r:
                            outcome = await r.json() if r.status == 200 else None

                        if not outcome or outcome.get("errorId") != 0:
                            raise RuntimeError("polling rejected")
                        if outcome.get("status") == "ready":
                            return outcome["solution"]["gRecaptchaResponse"]

                    raise TimeoutError("solver did not finish in time")
                except Exception as err:
                    print(f"[hcaptcha] attempt {attempt} failed: {err}")
                    await asyncio.sleep(1)
            return None

    async def solve(self, discord_headers, retries):
        discord_headers["Referer"] = self._oauth_endpoint
        self.refresh()
        if self.balance < _MIN_CREDIT:
            print("[hcaptcha] balance below minimum")
            return False

        async with aiohttp.ClientSession() as net:
            async with net.post(
                self._oauth_endpoint,
                json=self._oauth_body,
                headers=discord_headers,
                allow_redirects=True,
            ) as r:
                if r.status != 200:
                    print(f"[hcaptcha] oauth status {r.status}")
                    return False
                oauth_payload = await r.text()

            try:
                hop = json.loads(oauth_payload).get("location")
            except Exception as err:
                print(f"[hcaptcha] oauth parse failed: {err}")
                return False

            if hop:
                async with net.get(hop) as r:
                    if r.status != 200:
                        print(f"[hcaptcha] redirect status {r.status}")
                        return False

            async with net.get("https://owobot.com/captcha") as r:
                if r.status != 200:
                    print(f"[hcaptcha] captcha page status {r.status}")
                    return False

            async with net.get("https://owobot.com/api/auth") as r:
                if r.status != 200:
                    print(f"[hcaptcha] auth check status {r.status}")
                    return False
                if not await r.json():
                    print("[hcaptcha] empty auth payload")
                    return False

            token = await self._request_token(retries)
            if not token:
                print("[hcaptcha] no token produced")
                return False

            async with net.post(
                "https://owobot.com/api/captcha/verify",
                json={"token": token},
                headers={
                    "Referer": "https://owobot.com/captcha",
                    "Origin": "https://owobot.com",
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                },
            ) as r:
                if r.status == 200:
                    self.refresh()
                    return True
                print(f"[hcaptcha] verify status {r.status}: {await r.text()}")
                return False
