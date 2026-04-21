import aiohttp

url = "https://owobot.com/api/status"

def get_max_shards(json_data):
    max_shard = 0
    for item in json_data:
        if "shards" in item:
            shard_data = item["shards"]
            max_shard_in_item = max(shard["shard"] for shard in shard_data)
            if max_shard_in_item > max_shard:
                max_shard = max_shard_in_item
    return max_shard + 1

def get_shard_id(server_id, total_shards):

    e = int(server_id)
    """
    bin() returns binary of an int, 
    first two charactrer is removed since it starts with prefix '0b'
    """
    binary_str = bin(e)[2:]
    if len(binary_str) > 22:
        sliced_binary_str = binary_str[:-22]
    else:
        sliced_binary_str = '0'
    sliced_int = int(sliced_binary_str, 2)
    shard_id = sliced_int % total_shards
    return shard_id

async def delaycheck(session, server_id):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            json_data = await response.json()
    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")

    shard_id = get_shard_id(server_id, get_max_shards(json_data))

    for item in json_data:
        if "shards" in item:
            shard_data = item["shards"]
            for i in shard_data:
                if i["shard"] == shard_id:
                    return i
    return None

