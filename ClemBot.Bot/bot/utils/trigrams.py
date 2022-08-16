from typing import TypeAlias

import nltk

T_TRIGRAM_SET: TypeAlias = set[tuple[str, ...]]
T_SEARCH_BANK: TypeAlias = list[tuple[str, T_TRIGRAM_SET]]


class BankSearchEntry:
    __slots__ = ("item", "similarity")

    def __init__(self, item: str, similarity: float):
        self.item = item
        self.similarity = similarity

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BankSearchEntry):
            raise TypeError(
                f"Unsupported comparison between {BankSearchEntry.__qualname__} and {type(other).__qualname__}"
            )

        return self.similarity == other.similarity

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, BankSearchEntry):
            raise TypeError(
                f"Unsupported comparison between {BankSearchEntry.__qualname__} and {type(other).__qualname__}"
            )

        return self.similarity < other.similarity

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, BankSearchEntry):
            raise TypeError(
                f"Unsupported comparison between {BankSearchEntry.__qualname__} and {type(other).__qualname__}"
            )

        return self.similarity > other.similarity

    def __str__(self) -> str:
        return f"BankSearchEntry(item={self.item!r}, similarity={self.similarity:0.2f})"


def make_trigrams(item: str) -> T_TRIGRAM_SET:
    return set(nltk.trigrams(f"  {item}  "))


def compare(a: T_TRIGRAM_SET, b: T_TRIGRAM_SET) -> float:
    return len(a.intersection(b)) / (len(a) + 1e-10)


def similarity(a: T_TRIGRAM_SET, b: T_TRIGRAM_SET) -> float:
    return (compare(a, b) + compare(b, a)) / 2


def make_search_bank(items: list[str]) -> T_SEARCH_BANK:
    return [(item, make_trigrams(item)) for item in items]


def query_search_bank(bank: T_SEARCH_BANK, query: str) -> list[BankSearchEntry]:
    query_trgrms = make_trigrams(query)

    return sorted((BankSearchEntry(item, similarity(query_trgrms, item_trgrms)) for item, item_trgrms in bank), reverse=True)


def find_best_match(bank: T_SEARCH_BANK, query: str) -> BankSearchEntry:
    results = query_search_bank(bank, query)
    assert len(results) > 0
    return results[0]
