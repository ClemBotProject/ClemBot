import discord
import discord.ext.commands as commands

import bot.extensions as ext
from bot.consts import Colors


class BaseConverterCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @ext.group(pass_context=True, invoke_without_command=True, aliases=['convert', 'baseconvert'])
    @ext.long_help(
        'A simple base converter that takes in a base number an a value, '
        'then displays the value in binary, octal, decimal, and hexadecimal'
    )
    @ext.short_help('Mathematic base converter')
    @ext.example(('bconvert bin 11', 'bconvert hex 0xff'))
    async def bconvert(self, ctx) -> None:
        """
        A simple base converter that takes in a base number an a value, then displays the value in binary, octal, decimal, and hexadecimal

        Format: bconvert [base abbreviation OR full base name] [number OR number with base prefix]

                base abbreviations: [bin / dec / hex / oct]
                full base name: [binary / decimal / hexadecimal / oct]

                number examples: [11, 99, ff, 77 ]
                number with base prefix examples: [0b11, 99, 0xff, 0o77]
        """
        desc = 'Available Bases Include:\n binary (bin),\n decimal(dec),\n hexadecimal(hex),\n octal(oct)'
        embed = discord.Embed(title='Available Bases', description=desc, color=Colors.ClemsonOrange)
        await ctx.send(embed=embed)

    async def result(self, ctx, number) -> None:
        b = bin(number)
        d = int(number)
        h = hex(number)
        o = oct(number)

        attachment = discord.File(filename="Code.gif",
                                  fp="bot/cogs/base_converter/assets/Code.gif")

        embed = discord.Embed(title='Conversions', description=f'Numerical Conversions of {number}', color=Colors.ClemsonOrange)
        embed.set_thumbnail(url='attachment://Code.gif')
        embed.add_field(name='Binary', value=b, inline=False)
        embed.add_field(name='Decimal', value=d, inline=False)
        embed.add_field(name='Hexadecimal', value=h, inline=False)
        embed.add_field(name='Octal', value=o, inline=False)

        await ctx.send(embed=embed, file=attachment)

    @bconvert.command(pass_context=True, aliases=['binary'])
    async def bin(self, ctx, *, number) -> None:
        """
        Example: bconvert [bin / binary] [11 / 0b11]
        """
        number = int(number, 2)
        await self.result(ctx, number)

    @bconvert.command(pass_context=True, aliases=['decimal'])
    async def dec(self, ctx, *, number) -> None:
        """
        Example: bconvert [dec / decimal] [99]
        """
        number = int(number)
        await self.result(ctx, number)

    @bconvert.command(pass_context=True, aliases=['hexadecimal'])
    async def hex(self, ctx, *, number) -> None:
        """
        Example: bconvert [hex / hexadecimal] [FF / 0xFF]
        """
        number = int(number, 16)
        await self.result(ctx, number)

    @bconvert.command(pass_context=True, aliases=['octal'])
    async def oct(self, ctx, *, number) -> None:
        """
        Example: bconvert [oct / octal] [77 / 0o77]
        """
        number = int(number, 8)
        await self.result(ctx, number)


def setup(bot):
    bot.add_cog(BaseConverterCog(bot))
