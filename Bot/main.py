import discord
import ClemBot
import json
import logging
import sys
import logger as log

def main():

    log.setup_dis_py_log()

    secrets = {}

    try:
        log.botlog.info('Attempting to load BotSecrets.json')
        with open("BotSecrets.json") as f:
            lines = f.read()
            secrets = json.loads(lines)
            log.botlog.info('Bot Secrets Loaded')
    except FileNotFoundError as e:
        log.botlog.error(f'{e}: This means the bot could not find your BotSecrets Json File')
        sys.exit(0)
    except Exception as e:
        log.botlog.error(f'CONFIG ERROR: {e} ON STARTUP')
        sys.exit(0)

    log.botlog.info('Bot Starting Up')
    ClemBot.ClemBot(command_prefix = ':').run(secrets["BotToken"])


if __name__ == "__main__":
    main()


