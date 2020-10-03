import discord
import discord.ext.commands as commands

from bot.consts import Colors

class BaseConverterCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #if number less than <

    @commands.group()
    async def baseconvert(self, ctx):
        """
        A simple base converter that takes in a base number an a value, then displays the value in binary, octal, decimal, and hexadecimal
        Examples:
            baseconvert(bin 0b11010101)
            baseconvert(oct 0o1234)
            baseconvert(dec 4567)
            baseconvert(hex 0xAF13)
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid Subcommand!')

    @baseconvert.command()
    async def bin(self, ctx, number : str):
        number = int(number, 2)
        d = int(number)
        o = oct(number)	
        h = hex(number)
        if number in range(1114112): 
            a = chr(number)
        else:
            a = 'Unicode representation not found.'

        embed = discord.Embed(title='Conversions', description =f'Numerical Conversions of {number}', color = Colors.ClemsonOrange)
        embed.add_field(name='Decimal', value=d, inline=False)
        embed.add_field(name='Hexadecimal', value=h, inline=False)
        embed.add_field(name='Octal', value=o, inline=False)
        embed.add_field(name="UTF-8", value=a, inline=False)
        
        await ctx.send(embed=embed)
        
    @bin.error
    async def bin_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Input Binary is Invalid')
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send('Input Binary is Invalid')

    @baseconvert.command()
    async def dec(self, ctx, number : int):
        b = bin(number)
        h = hex(number)
        o = oct(number)
        if number in range(1114112):
            a = chr(number)
        else:
            a = 'Unicode representation not found.'

        embed = discord.Embed(title='Conversions', description =f'Numerical Conversions of {number}', color = Colors.ClemsonOrange)
        embed.add_field(name='Binary', value=b, inline=False)
        embed.add_field(name='Hexadecimal', value=h, inline=False)
        embed.add_field(name='Octal', value=o, inline=False)
        embed.add_field(name='UTF-8', value=a, inline=False)
        
        await ctx.send(embed=embed)

    @dec.error
    async def dec_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Input Decimal is Invalid')
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send('Input Decimal is Invalid')

    @baseconvert.command()
    async def hex(self, ctx, number : str):
        number = int(number, 16)
        b = bin(number)
        d = int(number)
        o = oct(number)

        if number in range(1114112):
            a = chr(number)
        else:
            a = 'Unicode representation not found.'

        embed = discord.Embed(title='Conversions', description =f'Numerical Conversions of {number}', color = Colors.ClemsonOrange)
        embed.add_field(name='Binary', value=b, inline=False)
        embed.add_field(name='Decimal', value=d, inline=False)
        embed.add_field(name='Octal', value=o, inline=False)
        embed.add_field(name='UTF-8', value=a, inline=False)
        
        await ctx.send(embed=embed)

    @hex.error
    async def hex_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Input Hexadecimal is Invalid')
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send('Input Hexadecimal is Invalid')

    @baseconvert.command()
    async def oct(self, ctx, number : str):
        number = int(number, 8)
        b = bin(number)
        d = int(number)
        h = hex(number)
        if number in range(1114112): 
            a = chr(number)
        else:
            a = 'Unicode representation not found.'

        embed = discord.Embed(title='Conversions', description =f'Numerical Conversions of {number}', color = Colors.ClemsonOrange)
        embed.add_field(name='Binary', value=b, inline=False)
        embed.add_field(name='Decimal', value=d, inline=False)
        embed.add_field(name='Hexadecimal', value=h, inline=False)
        embed.add_field(name='UTF-8', value=a, inline=False)
        
        await ctx.send(embed=embed)

    @oct.error
    async def oct_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Input Octal is Invalid')
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send('Input Octal is Invalid')

def setup(bot):
    bot.add_cog(BaseConverterCog(bot))