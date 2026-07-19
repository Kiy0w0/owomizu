# owomizu error relay

A tiny Cloudflare Pages Function that receives sanitized error reports from the bot and forwards them to a Discord webhook. The real Discord webhook URL lives only in Cloudflare environment variables, so it never ships inside the public repo and cannot be extracted from the client.

## How it works

```
bot  --POST /report (X-Mizu-Secret)-->  relay.kuromi.foo  --POST embed-->  Discord webhook (env var)
```

The relay checks a shared secret header, rate limits per IP, validates the payload shape, then forwards a compact embed to the webhook stored in `DISCORD_WEBHOOK_URL`.

## Deploy to Cloudflare Pages

1. Push this `relay/` folder to a repo (or connect the whole repo and set the build root to `relay`).
2. In Cloudflare dashboard: Pages, Create project, connect the repo.
3. Framework preset: none. Build command: empty. Output directory: `.` (Functions are auto-detected from the `functions/` folder).
4. Add a custom domain, for example `relay.kuromi.foo`.
5. Set these environment variables (Settings, Environment variables), for Production:
   - `MIZU_SECRET`: a long random string. Put the SAME value in the bot config `relaySecret`.
   - `DISCORD_WEBHOOK_URL`: your real Discord webhook URL. Never commit this.

The endpoint will be available at `https://relay.kuromi.foo/report`.

## Bot side config

In `config/global_settings.json` under `webhook.errorReport`:

```json
"errorReport": {
    "enabled": true,
    "mode": "relay",
    "relayUrl": "https://relay.kuromi.foo/report",
    "relaySecret": "same-value-as-MIZU_SECRET",
    "sanitize": true,
    "maxPerMinute": 5
}
```

Set `enabled` to `true` only if you want to send reports. Default is off.

## Security notes

- The webhook URL is server side only. Obfuscating it in the client would not protect it: anyone can deobfuscate a string or sniff outgoing traffic. The relay is the actual protection.
- The shared secret keeps casual abusers from posting to the relay. If it leaks, rotate `MIZU_SECRET` in Cloudflare and update client configs.
- Rate limiting is per IP and per instance. Cloudflare may run multiple instances, so treat it as best effort, not a hard cap.
- Reports are sanitized client side (home paths stripped, tokens and webhook URLs masked) before they leave the bot.
