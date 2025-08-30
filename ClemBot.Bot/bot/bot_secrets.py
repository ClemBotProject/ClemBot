import json
import os

from bot.errors import ConfigAccessError
from bot.utils.logging_utils import get_logger

log = get_logger(__name__)


class BotSecrets:
    def __init__(self) -> None:
        self._client_token: str | None = None
        self._client_secret: str | None = None
        self._bot_token: str | None = None
        self._bot_prefix: str | None = None
        self._repl_url: str | None = None
        self._github_url: str | None = None
        self._api_url: str | None = None
        self._api_key: str | None = None
        self._bot_only: bool | None = None
        self._startup_log_channel_ids: list[int] | None = None
        self._error_log_channel_ids: list[int] | None = None
        self._site_url: str | None = None
        self._docs_url: str | None = None
        self._allow_bot_input_ids: list[int] | None = None

    @property
    def client_token(self) -> str:
        if not self._client_token:
            raise ConfigAccessError("client_token has not been initialized")
        return self._client_token

    @client_token.setter
    def client_token(self, value: str | None) -> None:
        if self._client_token:
            raise ConfigAccessError("client_token has already been initialized")
        self._client_token = value

    @property
    def client_secret(self) -> str:
        if not self._client_secret:
            raise ConfigAccessError("client_secret has not been initialized")
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value: str | None) -> None:
        if self._client_secret:
            raise ConfigAccessError("client_secret has already been initialized")
        self._client_secret = value

    @property
    def bot_token(self) -> str:
        if not self._bot_token:
            raise ConfigAccessError("bot_token has not been initialized")
        return self._bot_token

    @bot_token.setter
    def bot_token(self, value: str | None) -> None:
        if self._bot_token:
            raise ConfigAccessError("bot_token has already been initialized")
        self._bot_token = value

    @property
    def bot_only(self) -> bool:
        if not self._bot_only:
            return False
        return self._bot_only

    @bot_only.setter
    def bot_only(self, value: bool) -> None:
        if self.bot_only:
            raise ConfigAccessError("bot_only has already been initialized")

        if isinstance(value, str):
            self._bot_only = bool(value)
        else:
            self._bot_only = value

    @property
    def bot_prefix(self) -> str:
        if not self._bot_prefix:
            return "!"
        return self._bot_prefix

    @bot_prefix.setter
    def bot_prefix(self, value: str | None) -> None:
        if self._bot_prefix:
            raise ConfigAccessError("bot_prefix has already been initialized")
        self._bot_prefix = value

    @property
    def github_url(self) -> str:
        if not self._github_url:
            return "https://github.com/ClemsonCPSC-Discord/ClemBot"
        return self._github_url

    @github_url.setter
    def github_url(self, value: str | None) -> None:
        if self._github_url:
            raise ConfigAccessError("github_url has already been initialized")
        self._github_url = value

    @property
    def repl_url(self) -> str:
        if not self._repl_url:
            raise ConfigAccessError("repl_url has not been intialized")
        return self._repl_url

    @repl_url.setter
    def repl_url(self, value: str | None) -> None:
        if self._repl_url:
            raise ConfigAccessError("repl_url has already been initialized")
        self._repl_url = value

    @property
    def startup_log_channel_ids(self) -> list[int]:
        if not self._startup_log_channel_ids:
            raise ConfigAccessError("startup_log_channel_ids has not been initialized")
        return self._startup_log_channel_ids

    @startup_log_channel_ids.setter
    def startup_log_channel_ids(self, value: list[int]) -> None:
        if self._startup_log_channel_ids:
            raise ConfigAccessError("startup_log_channel_ids has already been initialized")
        self._startup_log_channel_ids = value

    @property
    def error_log_channel_ids(self) -> list[int]:
        if not self._error_log_channel_ids:
            raise ConfigAccessError("error_log_channel_ids has not been initialized")
        return self._error_log_channel_ids

    @error_log_channel_ids.setter
    def error_log_channel_ids(self, value: list[int]) -> None:
        if self._error_log_channel_ids:
            raise ConfigAccessError("error_log_channel_ids has already been initialized")
        self._error_log_channel_ids = value

    @property
    def api_url(self) -> str:
        if not self._api_url:
            raise ConfigAccessError("api_url has not been initialized")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str | None) -> None:
        if self._api_url:
            raise ConfigAccessError("api_url has already been initialized")
        self._api_url = value

    @property
    def api_key(self) -> str:
        if not self._api_key:
            raise ConfigAccessError("api_key has not been initialized")
        return self._api_key

    @api_key.setter
    def api_key(self, value: str | None) -> None:
        if self._api_key:
            raise ConfigAccessError("api_key has already been initialized")
        self._api_key = value

    @property
    def site_url(self) -> str:
        if not self._site_url:
            raise ConfigAccessError("site_url has not been initialized")
        return self._site_url

    @site_url.setter
    def site_url(self, value: str | None) -> None:
        if self._site_url:
            raise ConfigAccessError("site_url has already been initialized")
        self._site_url = value

    @property
    def docs_url(self) -> str:
        if not self._docs_url:
            raise ConfigAccessError("docs_url has not been initialized")
        return self._docs_url

    @docs_url.setter
    def docs_url(self, value: str | None) -> None:
        if self._docs_url:
            raise ConfigAccessError("docs_url has already been initialized")
        self._docs_url = value

    @property
    def allow_bot_input_ids(self) -> list[int]:
        if self._allow_bot_input_ids is None:
            raise ConfigAccessError("allow_bot_input_ids has not been initialized")
        return self._allow_bot_input_ids

    @allow_bot_input_ids.setter
    def allow_bot_input_ids(self, value: list[int] | None) -> None:
        if self._allow_bot_input_ids:
            raise ConfigAccessError("allow_bot_input_ids has already been initialized")
        self._allow_bot_input_ids = value

    def load_development_secrets(self, lines: str) -> None:
        secrets = json.loads(lines)

        self.client_token = secrets["ClientToken"]
        self.client_secret = secrets["ClientSecret"]
        self.bot_token = secrets["BotToken"]
        self.bot_prefix = secrets["BotPrefix"]
        self.bot_only = secrets["BotOnly"]
        self.startup_log_channel_ids = secrets["StartupLogChannelIds"]
        self.error_log_channel_ids = secrets["ErrorLogChannelIds"]
        self.repl_url = secrets["ReplUrl"]
        self.github_url = secrets["GithubSourceUrl"]
        self.api_url = secrets["ApiUrl"]
        self.api_key = secrets["ApiKey"]
        self.site_url = secrets["SiteUrl"]
        self.docs_url = secrets["DocsUrl"]
        self.allow_bot_input_ids = secrets["AllowBotInputIds"]

        log.info("Bot Secrets Loaded")

    def load_production_secrets(self) -> None:

        # Ignore these type errors, mypy doesn't know how to handle properties that return narrower types then they are assigned too
        self.client_token = os.environ.get("CLIENT_TOKEN")
        self.client_secret = os.environ.get("CLIENT_SECRET")
        self.bot_token = os.environ.get("BOT_TOKEN")
        self.bot_prefix = os.environ.get("BOT_PREFIX")
        self.startup_log_channel_ids = [
            int(n) for n in os.environ.get("STARTUP_LOG_CHANNEL_IDS").split(",")  # type: ignore
        ]
        self.error_log_channel_ids = [
            int(n) for n in os.environ.get("ERROR_LOG_CHANNEL_IDS").split(",")  # type: ignore
        ]
        self.bot_only = os.environ.get("BOT_ONLY")  # type: ignore
        self.repl_url = os.environ.get("REPL_URL")
        self.github_url = os.environ.get("GITHUB_URL")
        self.api_url = os.environ.get("API_URL")
        self.api_key = os.environ.get("API_KEY")
        self.site_url = os.environ.get("SITE_URL")
        self.docs_url = os.environ.get("DOCS_URL")
        self.allow_bot_input_ids = [
            int(n) for n in os.environ.get("ALLOW_BOT_INPUT_IDS").split(",")  # type: ignore
        ]

        log.info("Production keys loaded")


secrets = BotSecrets()
