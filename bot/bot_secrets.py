import json
import logging

from bot.errors import ConfigAccessError

log = logging.getLogger(__name__)

class BotSecrets:

    __instance = None

    @staticmethod 
    def get_instance() -> 'BotSecrets':
        """ Static access method. """
        if BotSecrets.__instance is None:
            BotSecrets()
        return BotSecrets.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if BotSecrets.__instance is not None:
            raise Exception("BotSecrets is in singleton scope")
        else:
            BotSecrets.__instance = self
        self._clientToken = None
        self._clientSecret = None
        self._botToken = None
        self._databaseName = None

    @property
    def client_token(self) -> str:
        """
        The client api token defined in your developer page

        Raises:
            ConfigAccessError: Raised if the token has not been set

        Returns:
            str: The API Token
        """

        if not self._clientToken:
            raise ConfigAccessError(f'client_token has not been initialized')
        else:
            return self._clientToken

    @client_token.setter
    def client_token(self, value: str) -> None:
        if self._clientToken:
            raise ConfigAccessError(f'client_token has already been initialized')
        else:
            self._clientToken = value

    @property
    def client_secret(self) -> str:
        if not self._clientSecret:
            raise ConfigAccessError(f'client_secret has not been intialized')
        return self._clientToken

    @client_secret.setter
    def client_secret(self, value: str) -> None:
        if self._clientSecret:
            raise ConfigAccessError(f'client_secret has already been initialized')
        self._clientSecret = value

    @property
    def bot_token(self) -> str:
        """
        The discord api token defined in your discord developer page

        Raises:
            ConfigAccessError: Raised if the token has not been set

        Returns:
            str: The api Token
        """
        if not self._botToken:
            raise ConfigAccessError(f'bot_token has not been intialized')
        return self._botToken

    @bot_token.setter
    def bot_token(self, value: str) -> None:
        if self._botToken:
            raise ConfigAccessError(f'bot_token has already been initialized')
        self._botToken = value

    @property
    def database_name(self) -> str:
        if not self._databaseName:
            raise ConfigAccessError(f'database_name has not been intialized')
        return self._databaseName

    @database_name.setter
    def database_name(self, value: str) -> None:
        if self._databaseName:
            raise ConfigAccessError(f'database_name has already been initialized')
        self._databaseName = f'{value}.sqlite'

    def load_secrets(self, lines: str) -> None:
        secrets = json.loads(lines)
        log.info('Bot Secrets Loaded')
        
        self.client_token = secrets['ClientToken']
        self.client_secret = secrets['ClientSecret']
        self.bot_token = secrets['BotToken']
        self.database_name = secrets['DatabaseName'] if secrets['DatabaseName'] is None else 'ClemBot'
