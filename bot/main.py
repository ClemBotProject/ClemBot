import discord
from clem_bot import ClemBot as ClemBot
import logging
import sys
import os
from bot_secrets import BotSecrets

def setup_logger() -> None:

    handlers = []
    handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO, handlers=handlers)

def main():

    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    #sets up the logging for discord.py
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='Logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    
    #creates the logger for the Bot Itself
    setup_logger()
    bot_log = logging.getLogger('bot')
    bot_file_handle = logging.FileHandler('Logs/bot.log', encoding='utf-8', mode='w')
    bot_file_handle.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    bot_log.addHandler(bot_file_handle)

    try:
        bot_log.info('Attempting to load BotSecrets.json')
        with open("BotSecrets.json") as f:
            BotSecrets.load_secrets(f.read())

    except FileNotFoundError as e:
        bot_log.error(f'{e}: This means the bot could not find your BotSecrets Json File')
        sys.exit(0)
    except KeyError as e:
        bot_log.error(f'{e} is not a valid key in BotSecrets')
        sys.exit(0)

    bot_log.info('Bot Starting Up')
    ClemBot(command_prefix = ':').run(BotSecrets.BotToken)


if __name__ == "__main__":
    main()


