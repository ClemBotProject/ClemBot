import json
import logging
import typing as t

import aiohttp
import discord.ext.commands as commands
import discord.utils as utils

import bot.bot_secrets as bot_secrets
import bot.extensions as ext

log = logging.getLogger(__name__)

HEADERS = {
    'Content-type': 'application/json',
    'Accept': 'application/json'
}

MAX_CONTENT_LENGTH = 1900
MAX_LINE_LENGTH = 15
EVAL_COMMAND_COOLDOWN = 2


class EvalCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command(aliases=['e'])
    @commands.cooldown(1, EVAL_COMMAND_COOLDOWN, commands.BucketType.guild)
    @ext.long_help(
        'Allows for the evaluations of arbitrary python code directly in discord'
        'Supports all internal standard libraries like json or re'
    )
    @ext.short_help('Runs arbitrary python code in discord')
    @ext.example('eval print("hello world")')
    async def eval(self, ctx, *, code) -> None:
        code = code.replace('```python', '')
        code = code.replace('```py', '')
        code = code.replace('`', '')
        code = utils.escape_mentions(code)

        feedback_mes = await ctx.send('Code execution started')
        log.info('Code: {code} sent for evaluation by author: {author} in guild: {guild}',
                 code=code,
                 author=ctx.author.id,
                 guild=ctx.guild.id)

        output = await self._post_eval(code)
        stdout = output['stdout']
        stdout = stdout.strip('`')
        stdout = utils.escape_mentions(stdout)

        await feedback_mes.delete()

        if len(stdout) > MAX_CONTENT_LENGTH:
            await ctx.send(f'{ctx.author.mention} Attempted output length exceeds 2000 characters, Please try again')
            return

        result_emoji = ':white_check_mark:' if output['returncode'] == 0 else ':warning:'
        out = f'{ctx.author.mention}  {result_emoji} Eval Completed with response code: {output["returncode"]}'
        if stdout:
            await ctx.send(f'{out}\n\n```{self._format(stdout)}```')
        else:
            await ctx.send(f'{out}\n\n```[No Output]```')

    def _format(self, resp):
        lines = [f'{(i + 1):03d} | {line}' for i, line in enumerate(resp.split('\n')) if line]
        if len(lines) > MAX_LINE_LENGTH:
            lines = lines[:MAX_LINE_LENGTH]
            lines.append('... Output line limit exceeded, data truncated')
        return '\n'.join(lines)

    async def _post_eval(self, code) -> t.Union[str, None]:
        data = {
            "input": code
        }

        json_data = json.dumps(data)

        async with aiohttp.ClientSession() as s:
            async with s.post(bot_secrets.secrets.repl_url,
                              data=json_data,
                              headers=HEADERS) as resp:
                if resp.status == 200:
                    return json.loads(await resp.text())


def setup(bot):
    bot.add_cog(EvalCog(bot))
