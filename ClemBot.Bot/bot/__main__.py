import os
import logging
import sys

import discord

import bot.bot_secrets as bot_secrets
from bot.clem_bot import ClemBot
from bot.custom_prefix import CustomPrefix
from bot.messaging.messenger import Messenger
from bot.utils.scheduler import Scheduler


def main():
    bot_log = logging.getLogger()

    # check if this is a prod or a dev instance
    if bool(os.environ.get('PROD')):
        bot_log.info('Production env var found, loading production environment')
        bot_secrets.secrets.load_production_secrets()
    else:
        try:
            bot_log.info(f'Attempting to load BotSecrets.json from {os.getcwd()}')
            with open("BotSecrets.json") as f:
                bot_secrets.secrets.load_development_secrets(f.read())
        except FileNotFoundError as e:
            bot_log.fatal(f'{e}: The bot could not find your BotSecrets Json File')
            sys.exit(0)
        except KeyError as e:
            bot_log.fatal(f'{e} is not a valid key in BotSecrets')
            sys.exit(0)
        except Exception as e:
            bot_log.fatal(e)
            sys.exit(0)

    # get the default prefix for the bot instance
    prefix = bot_secrets.secrets.bot_prefix

    # Initialize the messenger here and inject it into the base bot class,
    # this is so it can be reused later on
    # if we decide to add something not related to the bot
    # E.G a website frontend
    messenger = Messenger(name='primary_bot_messenger')

    # create the custom prefix handler class
    custom_prefix = CustomPrefix(default=prefix)

    # enable privileged member gateway intents
    intents = discord.Intents.default() # pylint: disable=assigning-non-slot
    intents.members = True   # pylint: disable=assigning-non-slot

    # Create the scheduler for injection into the bot instance
    scheduler = Scheduler()

    # set allowed mentions
    mentions = discord.AllowedMentions(everyone=False, roles=False)

    bot_log.info('Bot Starting Up')
    ClemBot(
        messenger=messenger,
        scheduler=scheduler,
        command_prefix=custom_prefix.get_prefix,  # noqa: E126
        activity=discord.Game(name='https://clembot.io'),
        help_command=None,
        case_insensitive=True,
        max_messages=50000,
        allowed_mentions=mentions,
        intents=intents
    ).run(bot_secrets.secrets.bot_token)


if __name__ == '__main__':
    main()
