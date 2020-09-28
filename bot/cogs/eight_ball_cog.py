import discord
import discord.ext.commands as commands
from bot.consts import Colors

import time
import random

class EightBallCog(commands.Cog):
	@commands.command(aliases=['8ball',"🎱"])
	async def ball(self, ctx, *, question):
		"""
		A simple magic 8 ball than can be used with 'ball' or '8ball'
		Example:
			ball Will I have a good day today?
			8ball Will I have a bad day today?
			"""
		responses = [
			"It is certain.",
			"It is decidedly so.",
			"Without a doubt.",
			"Yes – definitely.",
			"You may rely on it.",
			"As I see it, yes.",
			"Most likely.",
			"Outlook good.",
			"Yes.",
			"Signs point to yes.",
			"Reply hazy, try again.",
			"Ask again later.",
			"Better not tell you now.",
			"Cannot predict now.",
			"Concentrate and ask again.",
			"Don't count on it.",
			"My reply is no.",
			"My sources say no.",
			"Outlook not so good.",
			"Very doubtful."
			]
		embed = discord.Embed(title="🎱", description= f"{random.choice(responses)}",color = Colors.ClemsonOrange)
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(EightBallCog(bot))
    