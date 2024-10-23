import discord
from discord import app_commands
from discord.ext import commands
from utils.logging import log
from utils.embeds import *
from typing import Optional
from utils.userdata import get_data_manager
from discord.app_commands import locale_str

class TestCreatorCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: testcreator loaded")

    @app_commands.command(name="testcmd", description="This is a testing command created with the cog curator.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def testcmd(self, interaction: discord.Interaction, bombs: int):
        pass

async def setup(client):
    await client.add_cog(TestCreatorCog(client))
