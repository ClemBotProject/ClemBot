import logging
import random
import asyncio

import discord
import discord.ext.commands as commands

from bot.consts import Colors

log = logging.getLogger(__name__)

class RandomCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def flip(self, ctx):

        random.seed(time.time())

        embed = discord.Embed(title='Coin Flip', color=Colors.ClemsonOrange)

        heads = discord.File(filename='Heads.jpg',
                             fp='bot/cogs/random_cog/assets/Heads.jpg')

        tails = discord.File(filename='Tails.jpg',
                             fp='bot/cogs/random_cog/assets/Tails.jpg')

        if random.randint(0, 1) == 1:
            attachment = heads
            embed.set_thumbnail(url='attachment://Heads.jpg')
        else:
            attachment = tails
            embed.set_thumbnail(url='attachment://Tails.jpg')

        await ctx.send(embed=embed, file=attachment)

    @commands.command(aliases = ['roll','dice'])
    async def diceroll(self, ctx, dice : str):
        """
        Rolls dice in a XdY format where X is the number of dice and Y is the number of sides on the dice.
            Example:
            1d6     -   Rolls 1 die with 6 sides
            2d8     -   Rolls 2 die with 8 sides
            3d10    -   Rolls 3 die with 10 sides
            4d20    -   Rolls 4 die with 20 sides
        """
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Entry has to be in a XdY format! See the help command for an example.')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))

        embed = discord.Embed(title ='Dice Roller', description = f'{ctx.message.author.mention} rolled **{dice}**', color = Colors.ClemsonOrange)
        embed.add_field(name ='Here are the results of their rolls: ', value = result, inline = False)
        await ctx.send(embed = embed)

    @commands.command(aliases=['8ball','🎱'])
    async def ball(self, ctx, *, question):
        """
        A simple magic 8 ball than can be used with 'ball' or '8ball'
        Example:
        ball Will I have a good day today?
        8ball Will I have a bad day today?
            """
        responses = [
            'It is certain.',
            'It is decidedly so.',
            'Without a doubt.',
            'Yes – definitely.',
            'You may rely on it.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Yes.',
            'Signs point to yes.',
            'Reply hazy, try again.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Concentrate and ask again.',
            'Don\'t count on it.',
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.'
            ]
        embed = discord.Embed(title='🎱', description= f'{random.choice(responses)}',color = Colors.ClemsonOrange)
        await ctx.send(embed=embed)

    @commands.command(aliases=['slotmachine','🎰'])
    async def slots(self, ctx):
        """
        A simple slot machine.
        """

        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)
        blank = '⬜'

        slotset = {a, b, c}

        if (len(slotset) == 1):
            message = f'{ctx.message.author.mention} won!'
        elif (len(slotset) == 2):
            message = f'{ctx.message.author.mention} almost won, 2/3!'
        else:
            message = f'{ctx.message.author.mention} lost, no matches.'

        slotstitle = '💎 Slot Machine 💎'

        async def slotsrolling(input, spinstatus,waittime):
            slotembed = discord.Embed(title = f'{slotstitle}', color = Colors.ClemsonOrange, description = f'**{ctx.message.author.name} has rolled the slots**')
            slotembed.add_field(name = input, value = spinstatus, inline = False)
            await asyncio.sleep(waittime)
            return slotembed

        embed = await slotsrolling(f'{blank} | {blank} | {blank}','Spinning',0)
        msg = await ctx.send(embed = embed)

        embed = await slotsrolling(f'{a} | {blank} | {blank}','Spinning',1.75)
        await msg.edit(embed = embed)

        embed = await slotsrolling(f'{a} | {b} | {blank}','Spinning',1.75)
        await msg.edit(embed = embed)

        embed = await slotsrolling(f'{a} | {b} | {c}', f'**{message}**',1.75)
        await msg.edit(embed = embed)

def setup(bot):
    bot.add_cog(RandomCog(bot))
