import json
import logging
log = logging.getLogger(__name__)

class BotSecrets:

    ClientToken = None
    ClientSecret = None
    BotToken = None
    DatabaseName = None

    @staticmethod
    def load_secrets(lines: str) -> None:
        secrets = json.loads(lines)
        log.info('Bot Secrets Loaded')
        
        BotSecrets.ClientToken = secrets['ClientToken']
        BotSecrets.ClientSecret = secrets['ClientSecret']
        BotSecrets.BotToken = secrets['BotToken']
        BotSecrets.DatabaseName = secrets['DatabaseName']


        