   

import asyncio

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def join_previous_giveaways(self):
        await self.bot.sleep_till(self.bot.settings_dict["defaultCooldowns"]["shortCooldown"])
        await self.bot.wait_until_ready()

        await self.bot.sleep_till(self.bot.settings_dict["defaultCooldowns"]["briefCooldown"])
        for i in self.bot.settings_dict["giveawayJoiner"]["channelsToJoin"]:
            try:
                channel = await self.bot.fetch_channel(i)
            except:
                channel = None
            if not channel:
                await self.bot.log(f"giveaway channel seems to be invalid", "#ff5f00")
                continue
            await self.bot.set_stat(False)
            async for message in channel.history(limit=self.bot.settings_dict["giveawayJoiner"]["messageRangeToCheck"]):
                if message.embeds:
                    for embed in message.embeds:
                        if embed.author.name is not None and " A New Giveaway Appeared!" in embed.author.name and message.channel.id in self.bot.settings_dict["giveawayJoiner"]["channelsToJoin"]:
                            await self.bot.sleep_till(self.bot.settings_dict["defaultCooldowns"]["briefCooldown"])
                            if message.components[0].children[0] and not message.components[0].children[0].disabled:
                                await message.components[0].children[0].click()
                                await self.bot.log(f"giveaway joined in {message.channel.name}", "#00d7af")

            await self.bot.set_stat(True)

    async def cog_load(self):
        if self.bot.settings_dict["giveawayJoiner"]["enabled"]:

            asyncio.create_task(self.join_previous_giveaways())
        else:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.giveaway"))
            except ExtensionNotLoaded:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.channel.id in self.bot.settings_dict["giveawayJoiner"]["channelsToJoin"]:
            if message.embeds:
                for embed in message.embeds:
                    if embed.author.name is not None and " A New Giveaway Appeared!" in embed.author.name and message.channel.id in self.bot.settings_dict["giveawayJoiner"]["channelsToJoin"]:
                        await self.bot.sleep_till(self.bot.settings_dict["giveawayJoiner"]["cooldown"])
                        if message.components[0].children[0] and not message.components[0].children[0].disabled:
                            await message.components[0].children[0].click()

async def setup(bot):
    await bot.add_cog(Giveaway(bot))