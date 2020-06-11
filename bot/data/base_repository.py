from bot.bot_secrets import BotSecrets
import logging
log = logging.getLogger(__name__)

class BaseRepository:

    def __init__(self):
        self.database_name = BotSecrets.get_instance().database_name
        self.resolved_db_path = f'database/{self.database_name}'

