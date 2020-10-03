import discord
import discord.ext.commands as commands

from bot.consts import Colors

class BaseConverterCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.group(aliases= ['convert','baseconvert'])
    async def bconvert(self, ctx, *args):
        """
        A simple base converter that takes in a base number an a value, then displays the value in binary, octal, decimal, and hexadecimal
        
            Examples:
            bconvert [bin / binary] [11 / 0b11]
            bconvert [dec / decimal] [99]
            bconvert [hex / hexadecimal] [FF / 0xFF]
            bconvert [oct / octal] [77 / 0o77]
        """
        base = args[0]
        number = args[1]
        if base is None or number is None:
            await ctx.send('Missing arguments! Use the help command for examples')
            return

        if base == 'bin' or base == 'binary':
            number = int(number, 2)

        elif base == 'dec' or base == 'decimal':
            number = int(number)

        elif base == 'hex' or base == 'hexadecimal':
            number = int(number, 16)

        elif base == 'oct' or base == 'octal':
            number = int(number, 8)

        else:
            await ctx.send('Invalid Entry! Use the help command for examples')
            return

        b = bin(number)
        d = int(number)
        h = hex(number)
        o = oct(number)	
        if number < 1114112: 
            a = chr(number)
        else:
            a = 'Unicode representation not found.'

        embed = discord.Embed(title='Conversions', description =f'Numerical Conversions of {number}', color = Colors.ClemsonOrange)
        embed.set_image(url = 'https://i.gifer.com/8oXf.gif')
        embed.add_field(name='Binary', value=b, inline=False)
        embed.add_field(name='Decimal', value=d, inline=False)
        embed.add_field(name='Hexadecimal', value=h, inline=False)
        embed.add_field(name='Octal', value=o, inline=False)
        embed.add_field(name="UTF-8", value=a, inline=False)
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(BaseConverterCog(bot))