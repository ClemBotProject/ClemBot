import asyncio
import typing as t

import discord

from bot.consts import Colors


class UserChoice:

    def __init__(self, ctx, *, timeout: float) -> None:
        self.ctx = ctx
        self.timeout = timeout

    async def send_confirmation(self, *, content: str = None, embed=None, is_error=False) -> bool:

        if embed and content:
            raise TypeError('Only specify the embed or the content, not both')

        if not embed and not content:
            raise TypeError('Content or embed must be specified')

        if not embed and content:
            embed = discord.Embed(title=content,
                                  color=Colors.ClemsonOrange if not is_error else Colors.Error)

        try:
            return bool(await self._send(embed, {1: '✅', 0: '❌'}))
        except asyncio.TimeoutError:
            return False

    async def _send(self,
                    embed: discord.Embed,
                    choices: t.Dict[t.Union[int, str], t.Union[discord.Emoji, str]]) -> t.Union[int, str]:

        msg = await self.ctx.send(embed=embed)

        # flip the keys and values so that we can return the key based on the
        # users emoji choice
        ret_dict = dict((v, k) for k, v in choices.items())

        for e in choices.values():
            await msg.add_reaction(e)

        def check(reaction, user) -> bool:
            return (
                    reaction.message.id == msg.id
                    and user == self.ctx.author
                    and reaction.emoji in choices.values()
            )

        try:
            reaction, _ = await self.ctx.cog.bot.wait_for('reaction_add', timeout=self.timeout, check=check)
            return ret_dict[reaction.emoji]
        except asyncio.TimeoutError:
            embed.add_field(name='Request Timeout:', value='User failed to respond in the alloted time', inline='false')
            await msg.edit(embed=embed)
            raise
        finally:
            await msg.delete()
