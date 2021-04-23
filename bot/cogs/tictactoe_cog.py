import asyncio
import random
import discord
import discord.ext.commands as commands

import bot.extensions as ext

class TicTacToeSetup:
    white_page = '⬜'
    X_Emoji = '❌'
    O_Emoji = '⭕'

    top_left = '↖️'
    top = '⬆️'
    top_right = '↗️'
    left = '⬅️'
    mid = '🟦'
    right = '➡️'
    bottom_left = '↙️'
    bottom = '⬇️'
    bottom_right = '↘️'

    #Creates the board
    @staticmethod
    def get_ttt_embed(player1, player2, data, move, final=False, tie=False):
        embed = discord.Embed(title=f"Match of {player1} vs {player2}")
        embed.colour = move.colour if not final else player1.colour if move == player2 else player2.colour
        data_ = data.copy()
        for i in range(1, 10):
            if data[i] == 0:
                data_[i] = TicTacToeSetup.white_page
            elif data[i] == 1:
                data_[i] = TicTacToeSetup.X_Emoji
            elif data[i] == 2:
                data_[i] = TicTacToeSetup.O_Emoji
        description = (
            f"{data_[1]}{data_[2]}{data_[3]}\n"
            f"{data_[4]}{data_[5]}{data_[6]}\n"
            f"{data_[7]}{data_[8]}{data_[9]}")
        if tie:
            description += f'\nMatch Draw!'
        elif not final:
            description += f'\n\n{move.name}\'s Turn'
            description += ' **(X)**' if move == player1 else ' **(O)**'
        else:
            if move == player1:
                description += f'\n\n{player2.name}#{player2.discriminator} is Winner.'
            else:
                description += f'\n\n{player1.name}#{player1.discriminator} is Winner.'

        embed.description = description
        return embed

    #Check for winner
    @staticmethod
    def declare_winner(data):
        game = []
        for i in [1, 4, 7]:
            row = []
            for j in range(i, i + 3):
                row.append(data[j])
            game.append(row)

        def declare(game_1):
            # horizontal
            for row_1 in game_1:
                if row_1.count(row_1[0]) == len(row_1) and row_1[0] != 0:
                    return row_1[0]
            # vertical
            for col in range(len(game[0])):
                check = []
                for row_2 in game:
                    check.append(row_2[col])
                if check.count(check[0]) == len(check) and check[0] != 0:
                    return check[0]

            # / diagonal
            diagonals = []
            for idx, reverse_idx in enumerate(reversed(range(len(game)))):
                diagonals.append(game[idx][reverse_idx])

            if diagonals.count(diagonals[0]) == len(diagonals) and diagonals[0] != 0:
                return diagonals[0]

            # \ diagonal
            diagonals_reverse = []
            for ix in range(len(game)):
                diagonals_reverse.append(game[ix][ix])

            if diagonals_reverse.count(diagonals_reverse[0]) == len(diagonals_reverse) and diagonals_reverse[0] != 0:
                return diagonals_reverse[0]
            return None

        winner = declare(game)
        return winner

class TicTacToeCog(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot;
    @ext.command(aliases=['tictactoe'],usage='[Member]')
    @ext.short_help('Mention an opponent to start a game!')
    @ext.long_help('Mention an opponent to start a game of tic-tac-toe')
    @ext.example('ttt @opponent')
    async def ttt(self, ctx, member: discord.Member):
        try:
            #EXCEPTIONS
            if member.bot:
                await ctx.send('The AI opponent is not yet implemented')
                return
            if member == ctx.author:
                await ctx.send('Get an actual opponent please')
                return

            message = await ctx.send(f"{member.mention} {ctx.author} wants to play 'Tic Tac Toe' with You. Accept/Deny by reacting on below buttons.")

            for r in ('✅','❎'):
                await message.add_reaction(r)

            confirmation = None

            def check(payload):
                nonlocal confirmation
                if payload.message_id != message.id or payload.user_id != member.id:
                    return False
                
                codeblock = str(payload.emoji)

                if codeblock not in ('✅','❎'):
                    return False
                
                if codeblock == '✅':
                    confirmation = True
                    return True

                elif codeblock == '❎':
                    confirmation = False
                    return True
                
            try:
                await self.bot.wait_for('raw_reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                confirmation = None

            if confirmation is None:
                return await ctx.send(f"{member} failed to accept your tic tac toe game challenge.")

            elif confirmation is False:
                return await ctx.send(f"{member} declined your tic tac toe game challenge.")

            # Choice of First Turn
            players_ = [ctx.author, member]
            player1, player1_move = random.choice(players_), 1
            player2, player2_move = players_[0] if players_.index(
                player1) == 1 else players_[1], 2
            data = {}
            for i in range(1, 10):
                data[i] = 0

            # Remaining Moves Dictionary
            remaining_moves = {
                TicTacToeSetup.top_left: 1, TicTacToeSetup.top: 2, TicTacToeSetup.top_right: 3,
                TicTacToeSetup.left: 4, TicTacToeSetup.mid: 5, TicTacToeSetup.right: 6,
                TicTacToeSetup.bottom_left: 7, TicTacToeSetup.bottom: 8, TicTacToeSetup.bottom_right: 9
            }

            move_of, move_name = player1, player1_move
            initial_embed = TicTacToeSetup.get_ttt_embed(
                player1, player2, data, move_of)
            initial_embed = await ctx.send(embed=initial_embed)

            # Add Emotes To Message (initial_embed)
            for emoji in remaining_moves.keys():
                await initial_embed.add_reaction(emoji)
            while True:

                def check(reaction_, user):
                    return user.id == move_of.id and initial_embed.id == reaction_.message.id

                # Wait for Reaction
                try:
                    reaction = await self.bot.wait_for('reaction_add', check=check, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.send('Timed Out..{} failed to use moves.'.format(move_of.mention))
                    return

                str_reaction = str(reaction[0])
                if str_reaction in remaining_moves.keys():
                    data[remaining_moves[str_reaction]] = move_name

                # Swap Turn
                move_of, move_name = (player1, player1_move) if move_of == player2 else (
                    player2, player2_move)

                # Generates Embed
                new_embed = TicTacToeSetup.get_ttt_embed(
                    player1, player2, data, move_of)

                # Removes current reaction from remaining moves dictionary.
                del remaining_moves[str_reaction]
                await initial_embed.edit(embed=new_embed)
                # Declaration of winner (Returns None if no one is Winner)
                winner = TicTacToeSetup.declare_winner(data)
                if winner is None:
                    # If moves still remaining
                    if len(remaining_moves.keys()) != 0:
                        await initial_embed.clear_reaction(str_reaction)
                    # Else Generates a Tie Embed
                    else:
                        await initial_embed.clear_reaction(str_reaction)
                        new_embed = TicTacToeSetup.get_ttt_embed(
                            player1, player2, data, move_of, tie=True)
                        await initial_embed.edit(embed=new_embed)
                        await ctx.send('Match Draw!')
                        return
                else:
                    # Generates a winner Embed
                    new_embed = TicTacToeSetup.get_ttt_embed(
                        player1, player2, data, move_of, final=True)
                    await initial_embed.edit(embed=new_embed)
                    if winner == 1:
                        await ctx.send(f'{player1.mention} is Winner.')
                    else:
                        await ctx.send(f'{player2.mention} is Winner.')
                    await initial_embed.clear_reactions()
                    return
        except discord.NotFound:
            return

def setup(bot):
    bot.add_cog(TicTacToeCog(bot))