import aiohttp

_STATUS_URL = "https://owobot.com/api/status"


def _max_shards(data: list) -> int:
    peak = 0
    for cluster in data:
        for shard in cluster.get("shards", []):
            if shard["shard"] > peak:
                peak = shard["shard"]
    return peak + 1


def _shard_for_guild(guild_id: int, total_shards: int) -> int:
    binary = bin(int(guild_id))[2:]
    trimmed = binary[:-22] if len(binary) > 22 else "0"
    return int(trimmed, 2) % total_shards


async def fetch_shard_status(session: aiohttp.ClientSession, guild_id: int) -> dict | None:
    try:
        async with session.get(_STATUS_URL, timeout=aiohttp.ClientTimeout(total=8)) as r:
            if r.status != 200:
                return None
            data = await r.json()
    except Exception:
        return None

    shard_id = _shard_for_guild(guild_id, _max_shards(data))

    for cluster in data:
        for shard in cluster.get("shards", []):
            if shard["shard"] == shard_id:
                return shard

    return None


async def is_owo_responsive(session: aiohttp.ClientSession, guild_id: int, max_latency_ms: int = 300) -> bool:
    shard = await fetch_shard_status(session, guild_id)
    if shard is None:
        return True
    latency = shard.get("latency", 0)
    return latency <= max_latency_ms
