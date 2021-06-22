from dataclasses import dataclass
from dataclasses_json import LetterCase, DataClassJsonMixin, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Tag(DataClassJsonMixin):
    name: str
    content: str
    creation_date: str
    guild_id: int
    user_id: int
    use_count: int = 0


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Infraction(DataClassJsonMixin):
    id: int
    guild_id: int
    author_id: int
    subject_id: int
    type: str
    reason: str
    duration: int
    time: str
    active: int
