import discord
from discord import app_commands
from discord.ext import commands
from utils.logging import log
from utils.embeds import *
from typing import Optional
from utils.userdata import get_data_manager
from discord.app_commands import locale_str

class EchoCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: echo loaded")

    @app_commands.command(name="echo", description="Echoes your input back out, with a notice that you posted it.")
    @app_commands.describe(
        message="The message to echo.",
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def echo(self, interaction: discord.Interaction, message: str):
        message = discord.utils.escape_mentions(message)
        await interaction.response.send_message(f"{message}\n-# echoed by {interaction.user.mention}")
        
async def setup(client):
    await client.add_cog(EchoCog(client))
