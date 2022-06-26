from typing import List, Set, Tuple
import nltk

TRIGRAM_SET = Set[Tuple[str]]


class BankSearchEntry:
    __slots__ = ('item', 'similarity')

    def __init__(self, item: str, similarity: float):
        self.item = item
        self.similarity = similarity

    def __eq__(self, other: object) -> bool:
        return self.similarity == getattr(other, 'similarity', other)

    def __lt__(self, other: object) -> bool:
        return self.similarity < getattr(other, 'similarity', other)

    def __gt__(self, other: object) -> bool:
        return self.similarity > getattr(other, 'similarity', other)


def make_trigrams(item: str) -> TRIGRAM_SET:
    return set(nltk.trigrams(f'  {item}  '))


def compare(a: TRIGRAM_SET, b: TRIGRAM_SET) -> float:
    return len(a.intersection(b)) / (len(a) + 1e-10)


def similarity(a: TRIGRAM_SET, b: TRIGRAM_SET) -> float:
    return (compare(a, b) + compare(b, a)) / 2


def make_search_bank(items: List[str]) -> List[Tuple[str, TRIGRAM_SET]]:
    return [(item, make_trigrams(item)) for item in items]


def find_best_match(bank: List[Tuple[str, TRIGRAM_SET]], query: str) -> BankSearchEntry:
    query_trgrms = make_trigrams(query)

    return max(
        [BankSearchEntry(item, similarity(query_trgrms, item_trgrms)) for item, item_trgrms in bank]
    )
