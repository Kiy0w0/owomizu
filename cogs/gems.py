import asyncio
import re
import time

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded


gem_tiers = {
    "common":    ["051", "065", "072", "079"],
    "uncommon":  ["052", "066", "073", "080"],
    "rare":      ["053", "067", "074", "081"],
    "epic":      ["054", "068", "075", "082"],
    "mythical":  ["055", "069", "076", "083"],
    "legendary": ["056", "070", "077", "084"],
    "fabled":    ["057", "071", "078", "085"],
}


def convert_small_numbers(small_number):
    numbers = {
        "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
        "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    }
    return int("".join(numbers.get(c, c) for c in small_number))


def find_gems_available(message):
    available_gems = {
        "fabled":    {"057": 0, "071": 0, "078": 0, "085": 0},
        "legendary": {"056": 0, "070": 0, "077": 0, "084": 0},
        "mythical":  {"055": 0, "069": 0, "076": 0, "083": 0},
        "epic":      {"054": 0, "068": 0, "075": 0, "082": 0},
        "rare":      {"053": 0, "067": 0, "074": 0, "081": 0},
        "uncommon":  {"052": 0, "066": 0, "073": 0, "080": 0},
        "common":    {"051": 0, "065": 0, "072": 0, "079": 0},
    }
    inv_numbers = re.findall(r"`(\d+)`.*?([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", message)
    for gem_id, small_number in inv_numbers:
        gem_count = convert_small_numbers(small_number)
        for _, gems in available_gems.items():
            if gem_id in gems:
                gems[gem_id] = gem_count
                break
    return available_gems


def len_gems_in_use(msg):
    return sum(1 for gem in ("gem1", "gem3", "gem4", "star") if gem in msg)


class Gems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.grouped_gems = None
        self.available_gems = {}
        self.inventory_check = False
        self.already_checked = False
        self.cache_gems_in_use = {}
        self.prev_count = 0
        self.count = 0

        self.gem_cmd = {
            "cmd_name": self.bot.alias["use"]["normal"],
            "cmd_arguments": "",
            "prefix": True,
            "checks": False,
            "id": "gems",
        }
        self.inv_cmd = {
            "cmd_name": self.bot.alias["inv"]["normal"],
            "prefix": True,
            "checks": True,
            "id": "inv",
        }

    def enabled_gem_types(self):
        cnf = self.bot.settings_dict["autoUse"]["gems"]["gemsToUse"]
        return {
            "huntGem":      cnf["huntGem"],
            "empoweredGem": cnf["empoweredGem"],
            "luckyGem":     cnf["luckyGem"],
            "specialGem":   cnf["specialGem"],
        }

    async def use_gems(self, available_gems, gems_in_use=None, full=False):
        if not full:
            result = self.find_specific_gems_to_use(gems_in_use, available_gems)
        else:
            result = self.find_gems_to_use(available_gems)

        if result:
            self.gem_cmd["cmd_arguments"] = ""
            for item in result:
                self.gem_cmd["cmd_arguments"] += f"{item[1:]} "
            await self.bot.log(f"Auto-using gems: {self.gem_cmd['cmd_arguments']} 💎", "#00d1d1")
            await self.bot.put_queue(self.gem_cmd, priority=True)
            self.reduce_used_gems(result)
            if getattr(self.bot, 'hunt_disabled', False):
                self.bot.hunt_disabled = False
        else:
            if not full:
                self.already_checked = True
            else:
                await self.bot.log("Warn: No gems to use.", "#924444")
                self.bot.user_status["no_gems"] = True
                if (
                    not getattr(self.bot, 'hunt_disabled', False)
                    and self.bot.settings_dict["autoUse"]["gems"]["disable_hunts_if_no_gems"]
                ):
                    await self.bot.log("Disabling hunt since there is no gems to be used.", "#C51818")
                    self.bot.hunt_disabled = True

    def fetch_gems_in_use(self, msg):
        gem_type_map = {
            "gem1": "huntGem",
            "gem4": "luckyGem",
            "gem3": "empoweredGem",
            "star": "specialGem",
        }
        tier_prefix_map = {
            "c": "common", "u": "uncommon", "r": "rare",
            "e": "epic", "m": "mythical", "l": "legendary", "f": "fabled",
        }

        result = []
        gems_in_use = []
        all_gem_type = ["huntGem", "luckyGem", "empoweredGem", "specialGem"]

        for key, value in gem_type_map.items():
            if key in msg:
                for prefix, tier in tier_prefix_map.items():
                    if f"{prefix}{key}" in msg:
                        result.append({"gem_type": value, "gem_tier": tier})
                        gems_in_use.append(value)

        gems_not_in_use = [x for x in all_gem_type if x not in gems_in_use]
        gems_required_to_use = self.enabled_gem_types()
        for gem in gems_not_in_use:
            if gems_required_to_use[gem]:
                return result, True

        return result, False

    def reduce_used_gems(self, used_gem_ids):
        for gem_id in used_gem_ids:
            for _, gems in self.available_gems.items():
                if gem_id in gems:
                    if gems[gem_id] > 0:
                        gems[gem_id] -= 1
                    if gems[gem_id] < 0:
                        gems[gem_id] = 0
                    break

    def find_gems_to_use(self, available_gems):
        gem_type = {0: "huntGem", 1: "empoweredGem", 2: "luckyGem", 3: "specialGem"}
        tier_order = ["fabled", "legendary", "mythical", "epic", "rare", "uncommon", "common"]
        cnf = self.bot.settings_dict["autoUse"]["gems"]

        if cnf["order"]["lowestToHighest"]:
            tier_order.reverse()

        grouped_gem_list = []
        for tier in tier_order:
            if not cnf["tiers"][tier]:
                continue
            current_group = []
            for gem_id in gem_tiers[tier]:
                gem_index = gem_tiers[tier].index(gem_id)
                gem_type_key = gem_type[gem_index]
                if (
                    cnf["gemsToUse"].get(gem_type_key)
                    and available_gems[tier].get(gem_id, 0) > 0
                ):
                    current_group.append(gem_id)
            if current_group:
                grouped_gem_list.append(current_group)

        return self.process_result(grouped_gem_list)

    def find_specific_gems_to_use(self, gems_in_use, available_gems):
        temp_available_gems = {tier: gems.copy() for tier, gems in available_gems.items()}
        gem_type_map = {
            "huntGem":      ["057", "056", "055", "054", "053", "052", "051"],
            "empoweredGem": ["071", "070", "069", "068", "067", "066", "065"],
            "luckyGem":     ["078", "077", "076", "075", "074", "073", "072"],
            "specialGem":   ["085", "084", "083", "082", "081", "080", "079"],
        }
        for item in gems_in_use:
            gem_ids = gem_type_map[item["gem_type"]]
            for _, gems in temp_available_gems.items():
                for gem_id in gem_ids:
                    if gem_id in gems:
                        gems[gem_id] = 0
        return self.find_gems_to_use(temp_available_gems)

    def process_result(self, result):
        return max(result, key=len, default=None)

    async def cog_load(self):
        if (
            not self.bot.settings_dict["commands"]["hunt"]["enabled"]
            or not self.bot.settings_dict["autoUse"]["gems"]["enabled"]
        ):
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.gems"))
            except ExtensionNotLoaded:
                pass
        else:
            await self.bot.log("Gem Automation Loaded 💎", "#00d1d1")

    async def cog_unload(self):
        await self.bot.remove_queue(id="gems")

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            message.channel.id != self.bot.channel_id
            or message.author.id != self.bot.owo_bot_id
        ):
            return

        nick = self.bot.get_nick(message)
        if nick not in message.content:
            return

        if "caught" in message.content:
            if self.bot.user_status["no_gems"]:
                return
            await self.bot.set_stat(False)
            self.inventory_check = True
            await self.bot.put_queue(self.inv_cmd, priority=True)

        if "hunt is empowered by" in message.content:
            if self.bot.user_status["no_gems"]:
                return
            if self.already_checked:
                count = len_gems_in_use(message.content)
                if count == self.count:
                    return
                else:
                    self.already_checked = False
                    self.count = count

            result, required = self.fetch_gems_in_use(message.content)
            if result and required:
                if self.available_gems:
                    await self.use_gems(self.available_gems, result)
                else:
                    await self.bot.set_stat(False)
                    await self.bot.put_queue(self.inv_cmd, priority=True)
                    self.cache_gems_in_use = result

        elif "'s Inventory ======**" in message.content:
            await self.bot.remove_queue(id="inv")
            self.available_gems = find_gems_available(message.content)
            self.already_checked = False

            if self.inventory_check:
                await self.use_gems(self.available_gems, full=True)
                await self.bot.sleep_till(
                    self.bot.settings_dict["defaultCooldowns"]["briefCooldown"]
                )
                self.inventory_check = False
                self.cache_gems_in_use = {}
            elif self.cache_gems_in_use:
                await self.use_gems(self.available_gems, self.cache_gems_in_use)
                self.cache_gems_in_use = {}

            await self.bot.set_stat(True)


async def setup(bot):
    await bot.add_cog(Gems(bot))