from datetime import datetime

import logging
import discord
import time
import math

from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.consts import DesignatedChannels
from bot.consts import Colors
from bot.data.designated_channel_repository import DesignatedChannelRepository

log = logging.getLogger(__name__)

# minimum reactions required to get on the starboard
# TODO: implement to where user-editable
MIN_REACTIONS = 1

# dictionary of rankings
RANKINGS = {
    0: "⭐ POPULAR",
    1: "🌟 QUALITY",
    2: "🥉 *THE PEOPLE HAVE SPOKEN*",
    3: "🥈 *INCREDIBLE*",
    4: "🥇 **LEGENDARY**",
    5: "🏆 ***GOD-TIER***",
}

class StarboardService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    async def load_service(self):
        pass

    # function to check to see if a reaction is legal
    def update_check(
        self,
        reaction: discord.Reaction,
        user: discord.User
    ) -> bool:

        # emote verification - stars only
        if str(reaction) != "⭐":
            return False

        # orignal poster reactions don't count
        if reaction.message.author == user:
            return False

        # bot messages don't count
        if reaction.message.author == self.bot.user:
            return False

        # minimum reactions
        if reaction.count < MIN_REACTIONS:
            return False

        # everything passes
        return True

    # message formatting function
    def make_message(self, message: discord.Message, stars: int) -> discord.Embed:

        title = f'{RANKINGS[math.floor((stars - MIN_REACTIONS) / MIN_REACTIONS)]} | {stars} Stars'

        embed = discord.Embed(
            title= title,
            color= Colors.Starboard,
            description= f'_Posted in #{message.channel}_ by {message.author.mention}'
        )

        embed.set_thumbnail(url= message.author.avatar_url_as(static_format='png'))
        embed.set_footer(text= f'Sent on {message.created_at.strftime("%m/%d/%Y")}')

        if len(message.content) > 0:
            embed.add_field(name= 'Message', value= message.content, inline= False)
    
        if len(message.attachments) > 0:
            embed.set_image(url= message.attachments[0].url)

        return embed

    # function to add an entry from the starboard
    async def add_to_starboard(self, reaction: discord.Reaction):

        # create message to send in the starboards
        starboard_message = self.make_message(reaction.message, reaction.count)

        #TODO: Add database insertion here, id, timestamp, stars, message id
        

        # send the message to #starboard
        await self.bot.messenger.publish(
            Events.on_send_in_designated_channel,
            DesignatedChannels.starboard,
            reaction.message.guild.id,
            starboard_message
        )

    """
    # function to delete an entry from the starboard
    async def delFromStarboard(self, message: discord.Message):
        
    # function to update an entry in the starboard
    async def updateMessage(self, message: discord.Message, numStars: int):

    # function to determine what to update, and how
    async def updateStarboardEntry(
        self,
        reaction: discord.Reaction,
        isAdding: bool
    ) -> None:

        # instace of the message reacted to and the number of stars
        msg = reaction.message
        numStars = reaction.count

        # if the reaction was added && number of stars is the threshold,
        # add message to starboard
        if isAdding and numStars == 1:
            addToStarboard(msg)
        
        # if reaction was added, update wall of fame messages
        elif isAdding:
            updateMessage(msg, numStars)

        # if reaction was removed but the number of stars is still above the
        # threshold, update the message
        elif (not isAdding) and numStars >= 1:
            updateMessage(msg, numStars)

        # otherwise, the messsage gets removed
        else:
            remove(msg)
    """

    @BaseService.Listener(Events.on_reaction_add)
    async def on_reaction_add(
        self,
        reaction: discord.Reaction,
        user: discord.User
    ) -> None:

        # check to see if the message is worthy
        if self.update_check(reaction, user):
            await self.add_to_starboard(reaction)
            # await self.updateStarboardEntry(reaction, True)

        else:
            pass