import logging
import discord
import time

from bot.messaging.events import Events
from bot.services.base_service import BaseService
from bot.consts import DesignatedChannels

log = logging.getLogger(__name__)

# minimum reactions required to get on the starboard
# TODO: implement to where user-editable
MIN_REACTIONS = 1

# dictionary of rankings
REACTIONS = {
    MIN_REACTIONS * 1: "⭐ POPULAR",                    # 1 * threshold
    MIN_REACTIONS * 2: "🌟 QUALITY",                    # 2 * threshold
    MIN_REACTIONS * 3: "🥉 *THE PEOPLE HAVE SPOKEN*",   # 3 * threshold
    MIN_REACTIONS * 4: "🥈 *INCREDIBLE*",               # 4 * threshold
    MIN_REACTIONS * 5: "🥇 **LEGENDARY**",              # 5 * threshold
    MIN_REACTIONS * 6: "🏆 ***GOD-TIER***",             # good luck getting here
}

class StarboardService(BaseService):

    def __init__(self, *, bot):
        super().__init__(bot)

    async def load_service(self):
        pass

    # function to check to see if a reaction is legal
    def additionCheck(
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

    # function to add an entry from the starboard
    async def addToStarboard(self, message: discord.Message):

        embed = discord.Embed(title='test')
        embed.add_field(name="CONTENT:", value=message.content)

        await self.bot.messenger.publish(
            Events.on_send_in_designated_channel,
            DesignatedChannels.starboard,
            message.guild.id,
            embed
        )

    """
    # function to delete an entry from the starboard
    async def delFromStarboard(self, message: discord.Message):
        
    # function to update an entry in the starboard
    async def updateMessage(self, message: discord.Message, numStars: int):
    """

    # function to determine what to update, and how
    async def updateStarboardEntry(
        self,
        reaction: discord.Reaction,
        isAdding: bool
    ) -> None:

        # instace of the message reacted to and the number of stars
        msg = reaction.message
        numStars = reaction.count

        """
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
        if self.additionCheck(reaction, user):
            await self.addToStarboard(reaction.message)

        else:
            return