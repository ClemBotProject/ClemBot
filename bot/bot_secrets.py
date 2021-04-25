import json
import logging
import os

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
        self._weather_key = None
        self._geocode_key = None
        self._merriam_key = None
        self._azure_translate_key = None

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
            return 'ClemBot'
        return self._database_name

    @database_name.setter
    def database_name(self, value: str) -> None:
        if self._database_name:
            raise ConfigAccessError(f'database_name has already been initialized')
        self._database_name = f'{value}.sqlite'

    @property
    def bot_prefix(self) -> str:
        if not self._bot_prefix:
            return '!'
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
            return 'https://github.com/ClemsonCPSC-Discord/ClemBot'
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

    @property
    def weather_key(self) -> str:
        if not self._weather_key:
            raise ConfigAccessError(f'weather_key has not been intialized')
        return self._weather_key

    @weather_key.setter
    def weather_key(self, value: str) -> None:
        if self._weather_key:
            raise ConfigAccessError(f'weather_key has already been initialized')
        self._weather_key = value

    @property
    def geocode_key(self) -> str:
        if not self._geocode_key:
            raise ConfigAccessError(f'geocode_key has not been intialized')
        return self._geocode_key

    @geocode_key.setter
    def geocode_key(self, value: str) -> None:
        if self._geocode_key:
            raise ConfigAccessError(f'geocode_key has already been initialized')
        self._geocode_key = value

    @property
    def azure_translate_key(self) -> str:
        if not self._azure_translate_key:
            raise ConfigAccessError(f'azure_translate_key has not been initialized')
        return self._azure_translate_key

    @azure_translate_key.setter
    def azure_translate_key(self, value: str) -> None:
        if self._azure_translate_key:
            raise ConfigAccessError(f'azure_translate_key has already been initialized')
        self._azure_translate_key = value

    def load_development_secrets(self, lines: str) -> None:
        secrets = json.loads(lines)
        log.info('Bot Secrets Loaded')

        self.client_token = secrets['ClientToken']
        self.client_secret = secrets['ClientSecret']
        self.bot_token = secrets['BotToken']
        self.database_name = secrets['DatabaseName']
        self.bot_prefix = secrets['BotPrefix']
        self.gif_me_token = secrets['GifMeToken']
        self.repl_url = secrets['ReplUrl']
        self.github_url = secrets['GithubSourceUrl']
        self.merriam_key = secrets['MerriamKey']
        self.weather_key = secrets['WeatherKey']
        self.geocode_key = secrets['GeocodeKey']
        self.azure_translate_key = secrets['AzureTranslateKey']

    def load_production_secrets(self) -> None:

        self.client_token = os.environ.get('CLIENT_TOKEN')
        self.client_secret = os.environ.get('CLIENT_SECRET')
        self.bot_token = os.environ.get('BOT_TOKEN')
        self.database_name = os.environ.get('DATABASE_NAME')
        self.bot_prefix = os.environ.get('BOT_PREFIX')
        self.gif_me_token = os.environ.get('GIF_ME_TOKEN')
        self.repl_url = os.environ.get('REPL_URL')
        self.github_url = os.environ.get('GITHUB_URL')
        self.merriam_key = os.environ.get('MERRIAM_KEY')
        self.weather_key = os.environ.get('WEATHER_KEY')
        self.geocode_key = os.environ.get('GEOCODE_KEY')
        self.azure_translate_key = os.environ.get('AZURE_TRANSLATE_KEY')

        log.info('Production keys loaded')
