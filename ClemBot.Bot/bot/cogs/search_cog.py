import logging
import re
import json
import aiohttp
import discord
import discord.ext.commands as commands
import bot.extensions as ext
from enum import Enum
from markdownify import markdownify
from urllib.parse import urlencode
from urllib.parse import unquote_plus
from bot.consts import Colors
from bot.messaging.events import Events

log = logging.getLogger(__name__)
max_related_topics = 5
image_url = 'https://duckduckgo.com'
search_url = 'https://api.duckduckgo.com/'
icon_url = 'https://i.imgur.com/Knq2kVa.png'
related_topics_pattern = re.compile('(https://duckduckgo.com/)([acdne]/)?(\\S+)', re.IGNORECASE)


class Category(Enum):
    ARTICLE = 'A', 'Article'
    DISAMBIGUATION = 'D', 'Disambiguation'
    CATEGORY = 'C', 'Category'
    NAME = 'N', 'Name'
    EXCLUSIVE = 'E', 'Exclusive'
    NONE = 'None', 'None'

    def code(self):
        return self.value[0]

    def name(self):
        return self.value[1]


class SearchResult:

    def __init__(self, json_response):
        self.json_response = json_response

    def __getitem__(self, item):
        return self.json_response

    def has_result(self):
        return len(self.json_response['Heading']) > 0

    def title(self):
        return self.json_response['Heading']

    def abstract(self):
        return markdownify(self.json_response['Abstract'])

    def category(self):
        return category_from_code(self.json_response['Type'])

    def has_thumbnail(self):
        return len(self.json_response['Image']) > 0

    def thumbnail(self):
        # surprisingly 'Image' in the JSON returns the latter half of the URL,
        # so we need to concat the other half, i.e., https://duckduckgo.com
        return image_url + self.json_response['Image']

    def related_topics(self) -> list:
        # related topics can return topics that we don't actually want,
        # so we're taking the subset of data that we can use and returning it
        topics = list()
        related_topics = self.json_response['RelatedTopics']
        for i in range(0, len(related_topics)):
            topic = related_topics[i]
            if 'FirstURL' not in topic:
                break
            topics.append(topic)
        return topics

    def has_related_topics(self):
        return len(self.related_topics()) > 0

    def related_topics_formatted(self):
        related_topics = self.related_topics()
        related_topics_formatted = list[str]()
        # maximum related topics can be changed in the global vars
        for i in range(0, min(max_related_topics, len(related_topics))):
            topic = related_topics[i]
            # stupid way of getting short related topics titles
            title = related_topics_pattern\
                .match(topic['FirstURL'])\
                .group(3)\
                .replace('_', ' ')
            title = unquote_plus(title)
            related_topics_formatted.append(f"[{title}]({topic['FirstURL']})")
        return '\n'.join(related_topics_formatted)

    def url(self):
        return self.json_response['AbstractURL']

    def source(self):
        return self.json_response['AbstractSource']


class SearchCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ext.command()
    @ext.short_help('Searches via DuckDuckGo.')
    @ext.long_help('Searches via DuckDuckGo\'s instant web API to bring up results from Wikipedia, wikiHow, and more.')
    @ext.example(['search clemson', 'search computer science', 'search how to tie a tie'])
    async def search(self, ctx, *, query: str):
        result = await self.duck_search(query)
        msg = await self.results(ctx, result) if result.has_result() else await self.no_results(ctx, query)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author, timeout=30)

    async def duck_search(self, query: str) -> SearchResult:
        data = urlencode({
            "q": query,
            "format": "json",
            "pretty": 1,
            "t": "ClemBot"
        })
        log.debug(f'Search URL: {search_url}?{data}')
        async with aiohttp.ClientSession() as session:
            # redirects should never happen so it's gonna be off by default just in case
            async with session.get(url=f'{search_url}?{data}', allow_redirects=False) as resp:
                response = json.loads(await resp.text())
            log.info(response)
        return SearchResult(response)

    async def results(self, ctx, result: SearchResult) -> discord.Message:
        embed = discord.Embed(title=f'{result.title()} - {result.category().name()}', color=Colors.ClemsonOrange,
                              description=result.abstract())
        embed.set_footer(text='Result provided by DuckDuckGo.', icon_url=icon_url)
        details = f'**Link**: [{result.title()}]({result.url()})\n'
        details += f'**Source**: {result.source()}'
        embed.add_field(name='Details', value=details, inline=False)
        if result.has_related_topics():
            embed.add_field(name='Related Topics', value=result.related_topics_formatted(), inline=False)
        if result.has_thumbnail():
            embed.set_thumbnail(url=result.thumbnail())
        return await ctx.send(embed=embed)

    async def no_results(self, ctx, query: str) -> discord.Message:
        embed = discord.Embed(title='No Results', color=Colors.Error,
                              description=f"Your query '{query}' yielded 0 results.")
        embed.set_footer(text='Result provided by DuckDuckGo.', icon_url=icon_url)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SearchCog(bot))


def category_from_code(code):
    for c in Category:
        if code == c.code():
            return c
    return Category.NONE
