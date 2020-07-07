import logging

from bot.bot_secrets import BotSecrets

log = logging.getLogger(__name__)

class BaseRepository:
    """
    The base level repository that defines the fully resolved path for
    sqlite connection
    """

    def __init__(self):
        self.database_name = BotSecrets.get_instance().database_name
        self.resolved_db_path = f'database/{self.database_name}'
