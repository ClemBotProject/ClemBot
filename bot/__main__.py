import logging
import os
import sys
from datetime import datetime

from bot.bot_secrets import BotSecrets
from bot.clem_bot import ClemBot as ClemBot


def setup_logger() -> None:

    handlers = []
    handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO, handlers=handlers)

def main():

    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    #sets up the logging for discord.py
    disc_log = logging.getLogger('discord')
    disc_log.setLevel(logging.DEBUG)
    disc_log_name = f'Logs/{datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}_discord.log'
    handler = logging.FileHandler(filename= disc_log_name, encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    disc_log.addHandler(handler)

    #creates the logger for the Bot Itself
    setup_logger()
    bot_log = logging.getLogger('bot')
    bot_log_name = f'Logs/{datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}_bot.log'
    bot_file_handle = logging.FileHandler(filename= bot_log_name, encoding='utf-8', mode='w')
    bot_file_handle.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    bot_log.addHandler(bot_file_handle)

    try:
        bot_log.info(f'Attempting to load BotSecrets.json from {os.getcwd()}')
        with open("BotSecrets.json") as f:
            BotSecrets.get_instance().load_secrets(f.read())
    except FileNotFoundError as e:
        bot_log.error(f'{e}: The bot could not find your BotSecrets Json File')
        sys.exit(0)
    except KeyError as e:
        bot_log.error(f'{e} is not a valid key in BotSecrets')
        sys.exit(0)
    except Exception as e:
        bot_log.error(e)

    token = os.environ.get('BotToken', None) 

    if token is not None:
        BotSecrets.get_instance().bot_token = token
    
    bot_log.info('Bot Starting Up')
    ClemBot(command_prefix = '$', max_messages= 5000).run(BotSecrets.get_instance().bot_token)


if __name__ == "__main__":
    main()
