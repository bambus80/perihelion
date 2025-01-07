import discord
from discord import app_commands
from discord.ext import commands
from utils.logging import log
from utils.embeds import *
from typing import Optional
from utils.userdata import get_data_manager
from discord.app_commands import locale_str

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
class GamesCog(commands.GroupCog, group_name="game"):
    def __init__(self, client):
        self.client = client
        self.ttt = client.get_cog('games/tictactoe')

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: games loaded")

    @app_commands.command(name="tictactoe")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def tictactoe(self, interaction: discord.Interaction, size: Optional[app_commands.Range[int, 3, 5]], row: Optional[app_commands.Range[int, 3, 5]], misere: Optional[bool] = False):
        """
        Creates a game of tic-tac-toe.

        Parameters
        ------------
        size: app_commands.Range[int, 3, 5]
            The size of the board. Ranges from 3 to 5.
        row: Optional[app_commands.Range[int, 3, 5]]
            The amount of letters in a row you need to win. Defaults to the board size, but can go down to 3.
        misere: Optional[bool]
            Inverts the winner and loser - if this is enabled, you want to **lose**!
        """
        if size is None:
            size = 3
        if row is None:
            row = size #its probably expected that the row length = the size
        if row > size:
            await interaction.response.send_message(embed=error_template("Row length has to be less than or equal to the board size!"))
        else:
            await interaction.response.send_message(f"Pick a place to start! {"Note that this game is in misere mode, so your goal is to lose!"}", view=self.ttt.TicTacToe(size, row, misere))

async def setup(client):
    await client.add_cog(GamesCog(client))
