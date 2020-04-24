import discord
from Bot.ClemBot import ClemBot as ClemBot
import logging
import sys
from Bot.BotSecrets import BotSecrets

def setup_logger(log_file, level=logging.INFO, StdOut=False) -> None:

    handlers = []
    handlers.append(logging.FileHandler(log_file, encoding='utf-8', mode='w'))
    handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO, handlers=handlers)

def main():

    #creates the logger for the Bot Itself
    setup_logger('Logs/bot.log', logging.INFO, True)

    log = logging.getLogger('main')

    #sets up the logging for discord.py
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='Logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    secrets = {}

    try:
        log.info('Attempting to load BotSecrets.json')
        with open("BotSecrets.json") as f:
            BotSecrets.load_secrets(f.read())

    except FileNotFoundError as e:
        log.error(f'{e}: This means the bot could not find your BotSecrets Json File')
        sys.exit(0)
    except KeyError as e:
        log.error(f'{e} is not a valid key in BotSecrets')
        sys.exit(0)

    log.info('Bot Starting Up')
    ClemBot(command_prefix = ':').run(secrets["BotToken"])


if __name__ == "__main__":
    main()


