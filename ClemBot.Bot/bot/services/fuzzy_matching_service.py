from bot.clem_bot import ClemBot
from bot.services.base_service import BaseService
from bot.utils.trigrams import find_best_match, make_search_bank, BankSearchEntry

    
class FuzzyMatchingService(BaseService):
    def __init__(self, bot: ClemBot):
        self.bot = bot

        self._cmd_name_bank = make_search_bank([cmd.name for cmd in bot.commands])

    async def load_service(self) -> None:
        pass

    def fuzzy_find_command(self, cmd_name: str) -> BankSearchEntry:
        return find_best_match(self._cmd_name_bank, cmd_name)
