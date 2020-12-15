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
        self._client_token = None
        self._client_secret = None
        self._bot_token = None
        self._database_name = None
        self._bot_prefix = None
        self._gifMe_token = None
        self._repl_url = None
        self._github_url = None
        self._merriam_key = None 

    @property
    def client_token(self) -> str:
        """
        The client api token defined in your developer page

        Raises:
            ConfigAccessError: Raised if the token has not been set

        Returns:
            str: The API Token
        """

        if not self._client_token:
            raise ConfigAccessError(f'client_token has not been initialized')
        else:
            return self._client_token

    @client_token.setter
    def client_token(self, value: str) -> None:
        if self._client_token:
            raise ConfigAccessError(f'client_token has already been initialized')
        else:
            self._client_token = value

    @property
    def client_secret(self) -> str:
        if not self._client_secret:
            raise ConfigAccessError(f'client_secret has not been intialized')
        return self._client_token

    @client_secret.setter
    def client_secret(self, value: str) -> None:
        if self._client_secret:
            raise ConfigAccessError(f'client_secret has already been initialized')
        self._client_secret = value

    @property
    def bot_token(self) -> str:
        """
        The discord api token defined in your discord developer page

        Raises:
            ConfigAccessError: Raised if the token has not been set

        Returns:
            str: The api Token
        """
        if not self._bot_token:
            raise ConfigAccessError(f'bot_token has not been intialized')
        return self._bot_token

    @bot_token.setter
    def bot_token(self, value: str) -> None:
        if self._bot_token:
            raise ConfigAccessError(f'bot_token has already been initialized')
        self._bot_token = value

    @property
    def database_name(self) -> str:
        if not self._database_name:
            raise ConfigAccessError(f'database_name has not been intialized')
        return self._database_name

    @database_name.setter
    def database_name(self, value: str) -> None:
        if self._database_name:
            raise ConfigAccessError(f'database_name has already been initialized')
        self._database_name = f'{value}.sqlite'

    @property
    def bot_prefix(self) -> str:
        if not self._bot_prefix:
            raise ConfigAccessError(f'bot_prefix has not been intialized')
        return self._bot_prefix

    @bot_prefix.setter
    def bot_prefix(self, value: str) -> None:
        if self._bot_prefix:
            raise ConfigAccessError(f'bot_prefix has already been initialized')
        self._bot_prefix = value
    
    @property
    def gif_me_token(self) -> str:
        if not self._gifMe_token:
            raise ConfigAccessError(f'gif_me has not been intialized')
        return self._gifMe_token

    @gif_me_token.setter
    def gif_me_token(self, value: str) -> None:
        if self._gifMe_token:
            raise ConfigAccessError(f'gif_me_token has already been initialized')
        self._gifMe_token = value

    @property
    def github_url(self) -> str:
        if not self._github_url:
            raise ConfigAccessError(f'github_url has not been intialized')
        return self._github_url

    @github_url.setter
    def github_url(self, value: str) -> None:
        if self._github_url:
            raise ConfigAccessError(f'github_url has already been initialized')
        self._github_url = value

    @property
    def repl_url(self) -> str:
        if not self._repl_url:
            raise ConfigAccessError(f'repl_url has not been intialized')
        return self._repl_url
        

    @repl_url.setter
    def repl_url(self, value: str) -> None:
        if self._repl_url:
            raise ConfigAccessError(f'repl_url has already been initialized')
        self._repl_url = value
    
    @property
    def merriam_key(self) -> str:
        if not self._merriam_key:
            raise ConfigAccessError(f'merriam_key has not been intialized')
        return self._merriam_key

    @merriam_key.setter
    def merriam_key(self, value: str) -> None:
        if self._merriam_key:
            raise ConfigAccessError(f'merriam_key has already been initialized')
        self._merriam_key = value

    def load_secrets(self, lines: str) -> None:
        secrets = json.loads(lines)
        log.info('Bot Secrets Loaded')
        
        self.client_token = secrets['ClientToken']
        self.client_secret = secrets['ClientSecret']
        self.bot_token = secrets['BotToken']
        self.database_name = secrets['DatabaseName'] or 'ClemBot'
        self.bot_prefix = secrets['BotPrefix'] or '!'
        self.gif_me_token = secrets['GifMeToken']
        self.repl_url = secrets['ReplUrl']
        self.github_url = secrets['GithubSourceUrl'] or 'https://github.com/ClemsonCPSC-Discord/ClemBot'
        self.merriam_key = secrets['MerriamKey']
