import discord
import ClemBot
import json
import logging
import sys

def main():

    setup_dis_py_log()
    botlog = setup_logger('botlog', 'Logs/bot.log', logging.INFO)
    botlog.info('Starting Up')

    secrets = {}

    try:
        botlog.info('Attempting to load BotSecrets.json')
        with open("BotSecrets.json") as f:
            lines = f.read()
            secrets = json.loads(lines)
    except FileNotFoundError as e:
        botlog.error(f'{e} This means the bot could not find your BotSecrets Json File')
        sys.exit(0)
    except Exception as e:
        botlog.error(f'CONFIG ERROR: {e} ON STARTUP')
        sys.exit(0)

    ClemBot.ClemBot().run(secrets["BotToken"])


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def setup_dis_py_log():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='Logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

if __name__ == "__main__":
    main()


