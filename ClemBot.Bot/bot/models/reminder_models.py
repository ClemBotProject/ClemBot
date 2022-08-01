import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from dataclasses_json import LetterCase, DataClassJsonMixin, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Reminder(DataClassJsonMixin):
    id: int
    link: str
    content: Optional[str]
    time: str
    dispatched: bool
    user_id: int
