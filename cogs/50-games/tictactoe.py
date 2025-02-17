from typing import Union, List

import discord
from discord import User, Member, app_commands
from discord.ext import commands
from utils.logging import log
from utils.translation import JSONTranslator

class TicTacToeCog(commands.Cog, name="games/tictactoe"):
    def __init__(self, client):
        self.client = client
        self.translator: JSONTranslator = client.tree.translator


    class TicTacToeButton(discord.ui.Button['TicTacToe']):
        def __init__(self, x: int, y: int, misere: bool):
            # A label is required, but we don't need one so a zero-width space is used
            # The row parameter tells the View which row to place the button under.
            # A View can only contain up to 5 rows -- each row can only have 5 buttons.
            # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
            super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
            self.x = x
            self.y = y
            self.misere = misere
            
        # This function is called whenever this particular button is pressed
        # This is part of the "meat" of the game logic
        async def callback(self, interaction: discord.Interaction):
            assert self.view is not None
            view: TicTacToeCog.TicTacToe = self.view
            state = view.board[self.y][self.x]
            if state in (view.X, view.O):
                return

            if view.current_player == view.X:
                if view.players[0] is None:
                    view.players[0] = interaction.user
                else:
                    if interaction.user != view.players[0]:
                        if interaction.user == view.players[1]:
                            await interaction.response.send_message("It's not your turn!",ephemeral=True)
                        else:
                            assert view.players[0] is not None and view.players[1] is not None
                            await interaction.response.send_message(f"{view.players[0].mention} and {view.players[1].mention} are already playing! Please wait for another game.", ephemeral=True)
                        return
                self.style = discord.ButtonStyle.danger
                self.label = 'X'
                self.disabled = True
                view.board[self.y][self.x] = view.X
                view.current_player = view.O
                content = "It's now O's turn."
            else:
                if view.players[1] is None:
                    view.players[1] = interaction.user
                else:
                    if interaction.user != view.players[1]:
                        if interaction.user == view.players[0]:
                            await interaction.response.send_message("It's not your turn!",ephemeral=True)
                        else:
                            assert view.players[0] is not None and view.players[1] is not None
                            await interaction.response.send_message(f"{view.players[1].mention} and {view.players[0].mention} are already playing! Please wait for another game.", ephemeral=True)
                        return
                self.style = discord.ButtonStyle.primary
                self.label = 'O'
                self.disabled = True
                view.board[self.y][self.x] = view.O
                view.current_player = view.X
                content = "It's now X's turn."

            winner = view.check_board_winner()
            if winner is not None:
                assert view.players[0] is not None and view.players[1] is not None
                if winner == view.X:
                    if self.misere: # we can just inverse the winner
                        content = f'O ({view.players[1].global_name}) won!'
                    else:
                        content = f'X ({view.players[0].global_name}) won!'
                elif winner == view.O:
                    if self.misere: # we can just inverse the winner
                        content = f'X ({view.players[0].global_name}) won!'
                    else:
                        content = f'O ({view.players[1].global_name}) won!'
                else:
                    content = "It's a tie!"

                for child in view.children:
                    child.disabled = True # pyright: ignore (the justification is that all children are going to be buttons)

                view.stop()

            await interaction.response.edit_message(content=content, view=view)


    class TicTacToe(discord.ui.View):
        X = -1
        O = 1
        Tie = 2

        def __init__(self, size, row, misere):
            super().__init__()
            self.size = size
            self.current_player = self.X
            self.misere = misere
            self.board = [x[:] for x in [[0] * size] * size]
            self.row = row
            self.players: List[Union[User, Member, None]] = [None, None]

            # Our board is made up of 3-5 by 3-5 TicTacToeButtons
            # The TicTacToeButton maintains the callbacks and helps steer
            # the actual game.
            for x in range(size):
                for y in range(size):
                    self.add_item(TicTacToeCog.TicTacToeButton(x, y, misere))

        # This method checks for the board winner -- it is used by the TicTacToeButton
        def check_board_winner(self):
            """Returns the 'mark' of the player with a row of the given length."""
            width = range(len(self.board))
            height = range(len(self.board[0]))
            # Do four scans across the board -- right, down, and diagonals.
            for dx, dy in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                edges = []
                if dx > 0:
                    # scanning right, start from left edge
                    edges += [(0, y) for y in height]
                if dy > 0:
                    # scanning down, start from top edge
                    edges += [(x, 0) for x in width]
                if dy < 0:
                    # scanning up, start from bottom edge
                    edges += [(x, height[-1]) for x in width]
                for ex, ey in edges:
                    mark = 0
                    row = 0
                    x, y = ex, ey
                    while x in width and y in height:
                        if self.board[x][y] == mark:
                            row += 1
                        else:
                            mark = self.board[x][y]
                            row = 1
                        if mark != 0 and row >= self.row:
                            return mark
                        x, y = x + dx, y + dy

            # If we're here, we need to check if a tie was made
            if all(i != 0 for row in self.board for i in row):
                return self.Tie

            return None


async def setup(client):
    await client.add_cog(TicTacToeCog(client))
