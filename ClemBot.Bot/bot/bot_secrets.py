import json
import logging
import typing as t
import os

from bot.errors import ConfigAccessError

log = logging.getLogger(__name__)


class BotSecrets:
    def __init__(self):
        self._client_token = None
        self._client_secret = None
        self._bot_token = None
        self._bot_prefix = None
        self._gifMe_token = None
        self._repl_url = None
        self._github_url = None
        self._merriam_key = None
        self._weather_key = None
        self._geocode_key = None
        self._merriam_key = None
        self._azure_translate_key = None
        self._api_url = None
        self._api_key = None
        self._bot_only = None
        self._startup_log_channel_ids = None
        self._error_log_channel_ids = None
        self._site_url = None
        self._docs_url = None

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
    def bot_only(self) -> bool:
        if not self._bot_only:
            return False
        return self._bot_only

    @bot_only.setter
    def bot_only(self, value) -> None:
        if self.bot_only:
            raise ConfigAccessError(f'bot_only has already been initialized')

        if isinstance(value, str):
            self._bot_only = bool(value)
        else:
            self._bot_only = value

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
            raise ConfigAccessError(f'gif_me has not been initialized')
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
            raise ConfigAccessError(f'weather_key has not been initialized')
        return self._weather_key

    @weather_key.setter
    def weather_key(self, value: str) -> None:
        if self._weather_key:
            raise ConfigAccessError(f'weather_key has already been initialized')
        self._weather_key = value

    @property
    def startup_log_channel_ids(self) -> t.List[int]:
        if not self._startup_log_channel_ids:
            raise ConfigAccessError(f'startup_log_channel_ids has not been initialized')
        return self._startup_log_channel_ids

    @startup_log_channel_ids.setter
    def startup_log_channel_ids(self, value: t.List[int]):
        if self._startup_log_channel_ids:
            raise ConfigAccessError(f'startup_log_channel_ids has already been initialized')
        self._startup_log_channel_ids = value

    @property
    def error_log_channel_ids(self) -> t.List[int]:
        if not self._error_log_channel_ids:
            raise ConfigAccessError(f'error_log_channel_ids has not been initialized')
        return self._error_log_channel_ids

    @error_log_channel_ids.setter
    def error_log_channel_ids(self, value: t.List[int]):
        if self._error_log_channel_ids:
            raise ConfigAccessError(f'error_log_channel_ids has already been initialized')
        self._error_log_channel_ids = value

    @property
    def geocode_key(self) -> str:
        if not self._geocode_key:
            raise ConfigAccessError(f'geocode_key has not been initialized')
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

    @property
    def api_url(self) -> str:
        if not self._api_url:
            raise ConfigAccessError(f'api_url has not been initialized')
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        if self._api_url:
            raise ConfigAccessError(f'api_url has already been initialized')
        self._api_url = value

    @property
    def api_key(self) -> str:
        if not self._api_key:
            raise ConfigAccessError(f'api_key has not been initialized')
        return self._api_key

    @api_key.setter
    def api_key(self, value: str) -> None:
        if self._api_key:
            raise ConfigAccessError(f'api_key has already been initialized')
        self._api_key = value

    @property
    def site_url(self) -> str:
        if not self._site_url:
            raise ConfigAccessError(f'site_url has not been initialized')
        return self._site_url

    @site_url.setter
    def site_url(self, value: str) -> None:
        if self._site_url:
            raise ConfigAccessError(f'site_url has already been initialized')
        self._site_url = value

    @property
    def docs_url(self) -> str:
        if not self._docs_url:
            raise ConfigAccessError(f'docs_url has not been initialized')
        return self._docs_url

    @docs_url.setter
    def docs_url(self, value: str) -> None:
        if self._docs_url:
            raise ConfigAccessError(f'docs_url has already been initialized')
        self._docs_url = value

    def load_development_secrets(self, lines: str) -> None:
        secrets = json.loads(lines)

        self.client_token = secrets['ClientToken']
        self.client_secret = secrets['ClientSecret']
        self.bot_token = secrets['BotToken']
        self.bot_prefix = secrets['BotPrefix']
        self.bot_only = secrets['BotOnly']
        self.startup_log_channel_ids = secrets['StartupLogChannelIds']
        self.error_log_channel_ids = secrets['ErrorLogChannelIds']
        self.gif_me_token = secrets['GifMeToken']
        self.repl_url = secrets['ReplUrl']
        self.github_url = secrets['GithubSourceUrl']
        self.merriam_key = secrets['MerriamKey']
        self.weather_key = secrets['WeatherKey']
        self.geocode_key = secrets['GeocodeKey']
        self.azure_translate_key = secrets['AzureTranslateKey']
        self.api_url = secrets['ApiUrl']
        self.api_key = secrets['ApiKey']
        self.site_url = secrets['SiteUrl']
        self.docs_url = secrets['DocsUrl']

        log.info('Bot Secrets Loaded')

    def load_production_secrets(self) -> None:

        self.client_token = os.environ.get('CLIENT_TOKEN')
        self.client_secret = os.environ.get('CLIENT_SECRET')
        self.bot_token = os.environ.get('BOT_TOKEN')
        self.bot_prefix = os.environ.get('BOT_PREFIX')
        self.startup_log_channel_ids = [int(n) for n in os.environ.get('STARTUP_LOG_CHANNEL_IDS').split(',')]
        self.error_log_channel_ids = [int(n) for n in os.environ.get('ERROR_LOG_CHANNEL_IDS').split(',')]
        self.bot_only = os.environ.get('BOT_ONLY')
        self.gif_me_token = os.environ.get('GIF_ME_TOKEN')
        self.repl_url = os.environ.get('REPL_URL')
        self.github_url = os.environ.get('GITHUB_URL')
        self.merriam_key = os.environ.get('MERRIAM_KEY')
        self.weather_key = os.environ.get('WEATHER_KEY')
        self.geocode_key = os.environ.get('GEOCODE_KEY')
        self.azure_translate_key = os.environ.get('AZURE_TRANSLATE_KEY')
        self.api_url = os.environ.get('API_URL')
        self.api_key = os.environ.get('API_KEY')
        self.site_url = os.environ.get('SITE_URL')
        self.docs_url = os.environ.get('DOCS_URL')

        log.info('Production keys loaded')


secrets = BotSecrets()
