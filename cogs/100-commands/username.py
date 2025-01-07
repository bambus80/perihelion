import discord
from discord import app_commands
from discord.ext import commands
from utils.logging import log
from utils.embeds import *
from typing import Optional
from utils.userdata import get_data_manager
from discord.app_commands import locale_str

from utils.roblox_usernames import get_random_username

class UsernameCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.language = client.get_cog('language')

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: username loaded")

    @app_commands.command(name="username", description="Generate a list of random usernames.")
    @app_commands.describe(
        count="The amount of usernames to generate.",
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def username(self, interaction: discord.Interaction, count: Optional[app_commands.Range[int, 1, 10]]):
        settings = get_data_manager("user", interaction.user.id)
        if count is None:
            count = 1
        await interaction.response.defer()
        usernames = []
        for i in range(count):
            usernames.append(get_random_username())
        if settings["Global: Compact mode"]:
            await interaction.followup.send(f"Username{self.language.s(count)} generated! | {self.language.list_format(usernames)}")
        else:
            await interaction.followup.send(embeds=[embed_template(f"Username{self.language.s(count)} generated!",
                                                                "\n".join(usernames))])
async def setup(client):
    await client.add_cog(UsernameCog(client))
