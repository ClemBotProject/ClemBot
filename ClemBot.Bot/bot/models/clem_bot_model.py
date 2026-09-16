from humps import camel
from pydantic import BaseModel, ConfigDict


class ClemBotModel(BaseModel):
    """Base model which adds support for camelCase"""

    model_config = ConfigDict(
        alias_generator=camel.case,
        populate_by_name=True,
        use_enum_values=True,
    )
