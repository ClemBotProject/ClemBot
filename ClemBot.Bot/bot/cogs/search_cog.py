import logging
import re
import json
import aiohttp
import discord
import discord.ext.commands as commands
import bot.extensions as ext
from markdownify import markdownify
from urllib.parse import urlencode
from urllib.parse import unquote_plus
from bot.consts import Colors
from bot.messaging.events import Events

log = logging.getLogger(__name__)
MAX_RELATED_TOPICS = 5
IMAGE_URL = 'https://duckduckgo.com'
SEARCH_URL = 'https://api.duckduckgo.com/'
ICON_URL = 'https://i.imgur.com/Knq2kVa.png'
RELATED_TOPICS_PATTERN = re.compile('(https://duckduckgo.com/)([acdne]/)?(\\S+)', re.IGNORECASE)
CATEGORIES = {
    'A': 'Article',
    'C': 'Category',
    'D': 'Disambiguation',
    'N': 'Name',
    'E': 'Exclusive'
}


class SearchResult:

    def __init__(self, json_response):
        self.json_response = json_response

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
        return IMAGE_URL + self.json_response['Image']

    def related_topics(self) -> list:
        # related topics can return topics that we don't actually want,
        # so we're taking the subset of data that we can use and returning it
        topics = list()
        related_topics = self.json_response['RelatedTopics']
        for topic in related_topics[0::]:
            if 'FirstURL' not in topic:
                break
            topics.append(topic)
        return topics

    def has_related_topics(self):
        return len(self.related_topics()) > 0

    def related_topics_formatted(self):
        related_topics = self.related_topics()
        related_topics_formatted = list()
        # maximum related topics can be changed in the global vars
        max_topics = min(MAX_RELATED_TOPICS, len(related_topics))
        for i, val in enumerate(related_topics):
            if i >= max_topics:
                break
            url = val['FirstURL']
            title = RELATED_TOPICS_PATTERN\
                .match(url)\
                .group(3)\
                .replace('_', ' ')
            title = unquote_plus(title)
            related_topics_formatted.append(f'[{title}]({url})')
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
    @ext.long_help("Searches via DuckDuckGo's instant web API to bring up results from Wikipedia, wikiHow, and more.")
    @ext.example(['search clemson', 'search computer science', 'search how to tie a tie'])
    async def search(self, ctx, *, query: str):
        result = await self.duck_search(query)
        msg = await self.results(ctx, result) if result.has_result() else await self.no_results(ctx, query)
        await self.bot.messenger.publish(Events.on_set_deletable, msg=msg, author=ctx.author, timeout=60)

    async def duck_search(self, query: str) -> SearchResult:
        data = urlencode({
            'q': query,
            'format': 'json',
            'pretty': 1,
            'skip_disambig': 1,
            't': 'ClemBot'
        })
        log.debug(f'Search URL: {SEARCH_URL}?{data}')
        async with aiohttp.ClientSession() as session:
            # redirects should never happen so it's gonna be off by default just in case
            async with session.get(url=f'{SEARCH_URL}?{data}', allow_redirects=False) as resp:
                response = json.loads(await resp.text())
        log.debug(response)
        return SearchResult(response)

    async def results(self, ctx, result: SearchResult) -> discord.Message:
        embed = discord.Embed(title=f'[{result.category()}] {result.title()} - {result.source()}',
                              color=Colors.ClemsonOrange,
                              description=f'{result.abstract()}\n\n**Link**: [{result.title()}]({result.url()})')
        embed.set_footer(text='Result provided by DuckDuckGo.', icon_url=ICON_URL)
        if result.has_related_topics():
            embed.add_field(name='Related Topics', value=result.related_topics_formatted(), inline=False)
        if result.has_thumbnail():
            embed.set_thumbnail(url=result.thumbnail())
        return await ctx.send(embed=embed)

    async def no_results(self, ctx, query: str) -> discord.Message:
        embed = discord.Embed(title='No Results', color=Colors.Error,
                              description=f"Your query '{query}' yielded 0 results.")
        embed.set_footer(text='Result provided by DuckDuckGo.', icon_url=ICON_URL)
        return await ctx.send(embed=embed)


def category_from_code(code: str):
    # going to capitalize it just in case
    code = code.upper()
    if code not in CATEGORIES:
        return 'None'
    return CATEGORIES[code]


def setup(bot):
    bot.add_cog(SearchCog(bot))
